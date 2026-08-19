"""
Script to set up a test database running with docker, for the customer class for instance using pytest


pytest configuration file. needs to be runned from project root


has db, has session

db.drop_all() ensures after each test a clean state every time

echo=True helps debug sql queries if needed

@pytest.fixture # decorators
a fixture provides a defined, reliable and consistent context for the tests. environment.
fixtures define the steps and data that constitute the arrange phase of a test
the services, state, or other operating environments set up by fixtures are accessed by test functions through arguments

-setup functions
-teardown functions

- pytest does not run with python REPL


"""

import os
import pytest

from app import create_app
from app.extensions import db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)

    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def db_(app):
    db.create_all()

    yield db

    db.drop_all()


@pytest.fixture(scope="function")
def session(db_):
    connection = db_.engine.connect()
    transaction = connection.begin()

    session = db_.session
    session.bind = connection

    yield session

    session.rollback()
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app):
    return app.test_client()
