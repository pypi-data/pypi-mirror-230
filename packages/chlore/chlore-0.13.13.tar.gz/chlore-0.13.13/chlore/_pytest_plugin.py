import os
import re
import pytest
import requests_mock
import requests

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.testclient import TestClient
from requests_mock import ANY

import chlore.database
from chlore.config import CONFIG
from chlore.app import app
from chlore.testing.dependencies import override_dependency


@pytest.fixture(scope="session")
def engine() -> Engine:
    "SQL Alchemy engine, configured using TEST_DATABASE_* env vars"
    if CONFIG.database is None:
        return None
    else:
        host = os.environ["TEST_DATABASE_HOST"]
        user = os.environ["TEST_DATABASE_USER"]
        password = os.environ["TEST_DATABASE_PASS"]
        return create_engine(f"mysql+pymysql://{user}:{password}@{host}/my_sap", pool_pre_ping=True)


@pytest.fixture
def session(engine):
    "SQL Alchemy session, tuned to be the same instance used by fastapi's dependency."
    connection = engine.connect()
    transaction = connection.begin()
    savepoint = connection.begin_nested()
    session = Session(bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint")
    with override_dependency(app, chlore.database.session, lambda: session):
        yield session
    session.close()
    transaction.rollback()
    connection.close()


def truncate_tables(engine):
    with Session(engine, expire_on_commit=False) as session:
        session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for table in chlore.database.metadata.tables:
            session.execute(text(f"TRUNCATE TABLE `{table}`;"))
        session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        session.commit()


@pytest.fixture(scope="session", autouse=True)
def fresh_database(engine):
    if CONFIG.database is None:
        yield None
    else:
        chlore.database.metadata.create_all(engine)
        yield
        truncate_tables(engine)


@pytest.fixture(scope="module")
def test_client():
    "A fastapi.TestClient instance for this app."
    with TestClient(app) as client:
        yield client


def _url_for(base, **params):
    """Contruct urls with query arguments the same way requests does.
    This is a workaround needed to mock requests with arguments, as the code in
    requests_mock expects the query argument in the url to be in the exact same
    order both in the requests and in the mock definition.
    """
    request = requests.Request("GET", base, params=params).prepare()
    return request.url


@pytest.fixture
def http_mock(test_client, requests_mock):
    "requests_mock.Mocker instance tuned to not interfere with fastapi.TestClient."
    # we need to whitelist the fastapi TestClient's base url.
    base_url_re = re.escape(str(test_client.base_url))
    matcher = re.compile(rf"{base_url_re}(/.*)?")
    requests_mock.register_uri(ANY, matcher, real_http=True)
    requests_mock.url_for = _url_for
    return requests_mock
