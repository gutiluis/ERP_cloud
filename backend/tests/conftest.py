#!/bin/env python

'''
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


'''

import pytest
from app import create_app
from app.extensions import db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://erp:erp@127.0.0.1:3307/erp_test"
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
    connection = db.engine.connect()
    transaction = connection.begin()

    session = db.session
    session.bind = connection

    yield session

    session.rollback()
    transaction.rollback()
    connection.close()
