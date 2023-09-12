import os
from contextlib import contextmanager

from pydantic import BaseSettings

from chlore.config import CONFIG, DatabaseConfig, from_env


@contextmanager
def push_env(values: dict):
    old_env = os.environ.copy()
    for k, v in values.items():
        os.environ[k] = v
    yield os.environ
    os.environ = old_env


def test_from_env_without_prefix():
    with push_env({"URL": "some://url"}):
        database = from_env(DatabaseConfig)
        assert database.url == "some://url"


def test_from_env_with_prefix():
    with push_env({"DATABASE_URL": "some://url"}):
        database = from_env(DatabaseConfig, with_prefix="DATABASE_")
        assert database.url == "some://url"


class OtherConfig(BaseSettings):
    url: str


def test_from_env_registration():
    with push_env({"URL": "some://url"}):
        other = from_env(OtherConfig)
        assert other.url == "some://url"

    with push_env({"URL": "some://url"}):
        database = from_env(DatabaseConfig)
        assert database.url == "some://url"
        assert CONFIG.database is database
