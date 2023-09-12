from dataclasses import dataclass
from typing import Literal, Type, TypeVar, get_type_hints

from pydantic import BaseSettings


class ConfigError(Exception):
    pass


class AuthConfig(BaseSettings):
    url: str
    cookie_domain: str
    pubkey_path: str


class DatabaseConfig(BaseSettings):
    url: str


class LoggingConfig(BaseSettings):
    format: Literal["console", "json"] = "console"


class RabbitMQConfig(BaseSettings):
    url: str


class CORSConfig(BaseSettings):
    allowed_origin_re: str = ""


AnyConfig = TypeVar("AnyConfig", bound=BaseSettings)
ChloreConfig = TypeVar("ChloreConfig", AuthConfig, CORSConfig, DatabaseConfig, LoggingConfig, RabbitMQConfig)


@dataclass
class _InternalConfig:
    auth: AuthConfig = None
    cors: CORSConfig = None
    logging: LoggingConfig = None
    database: DatabaseConfig = None
    rabbitmq: RabbitMQConfig = None

    def wants(self, type: Type[AnyConfig]) -> bool:
        return type in ChloreConfig.__constraints__

    def register(self, type: Type[ChloreConfig], value: ChloreConfig):
        table = {type: field_name for field_name, type in get_type_hints(_InternalConfig).items()}
        setattr(self, table[type], value)


CONFIG = _InternalConfig()


def from_env(t: Type[AnyConfig], with_prefix: str = "") -> AnyConfig:
    class WithPrefix(t):
        class Config:
            env_prefix = with_prefix

    result = WithPrefix()
    if CONFIG.wants(t):
        CONFIG.register(t, result)
    return result
