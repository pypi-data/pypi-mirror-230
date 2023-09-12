from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from chlore.etna_auth import Identity, identity, any_auth, requires_adm, fake_identity


def test_auth():
    app = FastAPI()
    client = TestClient(app)

    @app.get("/any_auth")
    def any_auth_endpoint(identity: dict = Depends(identity)):
        return "OK"

    @app.get("/adm_only", dependencies=[Depends(any_auth), Depends(requires_adm)])
    def adm_only_endpoint():
        return "OK"

    r = client.get("/any_auth")
    assert r.status_code == 401
    ident1 = Identity(
        login="student_s", id=1, groups=["student"], email="student_s@staging.etna.io", login_date="", logas=False
    )
    ident2 = Identity(login="adm_a", id=2, groups=["adm"], email="adm_a@staging.etna.io", login_date="", logas=False)
    with fake_identity(app, ident1):
        r = client.get("/any_auth")
        assert r.status_code == 200
        r = client.get("/adm_only")
        assert r.status_code == 403
    r = client.get("/any_auth")
    assert r.status_code == 401
