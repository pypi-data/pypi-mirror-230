import base64
from contextlib import contextmanager
from functools import cache
import json
from pathlib import Path
import urllib.parse

from fastapi import FastAPI, Cookie, Depends, Header, HTTPException, params
from fastapi.requests import Request
import OpenSSL
import pydantic
import structlog
import requests

from chlore.config import CONFIG
from chlore.logging import request_logger

logger = structlog.get_logger("chlore.auth")


class InvalidToken(Exception):
    pass


def _parse_and_verify_etna_token(raw_token: str, cert: OpenSSL.crypto.X509 | None) -> dict:
    try:
        decoded = json.loads(base64.b64decode(raw_token))
        identity = decoded["identity"]
        signature = decoded["signature"]
    except Exception as e:
        raise InvalidToken("cannot parse etna auth token") from e

    try:
        if cert is not None:
            OpenSSL.crypto.verify(cert, base64.b64decode(signature), identity.encode(), "sha1")
    except Exception as e:
        raise InvalidToken("etna auth token verification failed") from e

    try:
        return json.loads(base64.b64decode(identity))
    except Exception as e:
        raise InvalidToken("cannot parse etna auth identity") from e


@cache
def _load_auth_key():
    """
    Load the public key from Config.auth.pubkey_path into a X509 signing certificate.
    """

    path = Path(CONFIG.auth.pubkey_path)
    logger.info("Loading auth signing certificates", path=str(path))
    if path == "/dev/null":
        return None
    content = path.read_text()
    pubkey = OpenSSL.crypto.load_publickey(OpenSSL.crypto.FILETYPE_PEM, content)
    cert = OpenSSL.crypto.X509()
    cert.set_pubkey(pubkey)
    return cert


def _extract_cookie_token(authenticator: str = Cookie(default=None)) -> str | None:
    if authenticator is not None:
        return urllib.parse.unquote_plus(authenticator)
    return None


def _extract_header_token(authorization: str = Header(default=None)) -> str | None:
    if authorization is not None:
        token = authorization.split("Legacy ")[-1]
        if token and len(token) != len(authorization):
            return token
    return None


def _extract_any_token(
    cookie_token: str = Depends(_extract_cookie_token),
    header_token: str = Depends(_extract_header_token),
) -> str | None:
    return cookie_token or header_token or None


def _add_identity(request: Request, token: str | None):
    if token is not None:
        cert = _load_auth_key()
        try:
            request.state.identity = _parse_and_verify_etna_token(token, cert)
            request.state.token = token
        except InvalidToken as e:
            request_logger().exception("cannot parse legacy auth token")
            # We want a 400 (validation error) instead of a 401 here. This avoid
            # a redirection loop to the login page, and provides the user with a nice
            # explaination why that request cannot be fullfiled. As this scenario (an
            # invalid token) is more likely to arise in dev, this seems to be the most
            # sensible status.
            raise HTTPException(400, detail="invalid auth token") from e


def any_auth(request: Request, token: str | None = Depends(_extract_any_token)):
    _add_identity(request, token)


def cookie_auth(request: Request, token: str | None = Depends(_extract_cookie_token)):
    _add_identity(request, token)


def header_auth(request: Request, token: str | None = Depends(_extract_header_token)):
    _add_identity(request, token)


class Logas(pydantic.BaseModel):
    login: str
    id: int
    roles: list[str]
    email: str
    login_date: str

    @pydantic.root_validator(pre=True)
    def _rename_groups_to_roles(cls, values):
        values["roles"] = values.get("groups", [])
        return values


class Identity(pydantic.BaseModel):
    login: str
    id: int
    roles: list[str]
    email: str
    login_date: str
    logas: bool | Logas

    @pydantic.root_validator(pre=True)
    def _rename_groups_to_roles(cls, values):
        values["roles"] = values.get("groups", [])
        return values

    def has_role(self, role):
        return role in self.roles

    def ensure_has_role(self, role):
        "Raise HTTPException(403) unless this identity has given role"
        if not self.has_role(role):
            raise HTTPException(403, detail="permission denied")


def identity(request: Request) -> Identity:
    identity = getattr(request.state, "identity", None)
    if identity is None:
        raise HTTPException(401, detail="unauthorized")
    return Identity(**identity)


def _request_token(request: Request) -> str:
    token = getattr(request.state, "token", None)
    if token is None:
        raise HTTPException(401, detail="unauthorized")
    return token


class RolesAllowed:
    def __init__(self, *roles: str):
        self.roles_allowed = roles

    def __call__(self, identity: Identity = Depends(identity)):
        if any(identity.has_role(role) for role in self.roles_allowed):
            return self.roles_allowed
        raise HTTPException(403, detail="permission denied")


requires_adm = RolesAllowed("adm")


@contextmanager
def fake_identity(app: FastAPI, wanted_identity: Identity):
    try:
        app.dependency_overrides[identity] = lambda: wanted_identity
        app.dependency_overrides[EtnaToken.from_request] = lambda: ""
        yield wanted_identity
    finally:
        if identity in app.dependency_overrides:
            del app.dependency_overrides[identity]
        if EtnaToken.from_request in app.dependency_overrides:
            del app.dependency_overrides[EtnaToken.from_request]


class EtnaToken:
    """
    Abstraction over ETNA authentication information needed to use Etna APIs and services.

    It can be constructed from multiple sources, such as an HTTP request or a raw base64-encoded token.
    """

    def __init__(self, value: str):
        self.value = value

    @property
    def as_base64(self) -> str:
        return self.value

    @classmethod
    def from_base64(cls, token: str) -> "EtnaToken":
        """
        Construct an EtnaToken from a raw base64-encoded token
        """
        return cls(token)

    @classmethod
    def from_request(cls, request: Request) -> "EtnaToken":
        """
        Construct an EtnaToken from a given request (or raise an HTTPException(401) if the request is unauthenticated)
        """
        return cls(_request_token(request))

    @classmethod
    def from_login_and_password(cls, login, password):
        try:
            auth_url = CONFIG.auth.url.rstrip("/") + "/identity"
            login_form = dict(login=login, password=password)
            response = requests.post(auth_url, data=login_form)
            if response.status_code == 200:
                return cls.from_base64(response.cookies["authenticator"])
            else:
                logger.warning(f"auth login failed", url=auth_url, login=login, status=response.status_code)
        except Exception as E:
            logger.exception(f"failed to login against legacy auth", url=auth_url, login=login)
            raise
        return cls()  # will raise an exception as there is no credential provided.
