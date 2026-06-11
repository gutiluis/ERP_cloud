#!/bin/env python

'''
Tests for the User model using pytest and the test DB (e.g. Docker).

- Use the session fixture; do not use db.session directly in tests.
- Ensure tests/ has __init__.py so it is recognized as a package.
'''

import pytest
from app.models.user import User
from app.extensions import db


def test_create_user(session):
    """Create a user with required fields and check defaults."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        password_hash="hashed_password_here",
    )
    session.add(user)
    session.commit()

    retrieved = session.query(User).filter_by(username="testuser").first()
    assert retrieved is not None
    assert retrieved.username == "testuser"
    assert retrieved.email == "testuser@example.com"
    assert retrieved.password_hash == "hashed_password_here"
    assert retrieved.is_active is True
    assert retrieved.is_admin is False
    assert retrieved.additional_notes is None


def test_create_user_with_optionals(session):
    """Create a user with optional fields set."""
    user = User(
        username="adminuser",
        email="admin@example.com",
        password_hash="admin_hash",
        is_active=True,
        is_admin=True,
        additional_notes="VIP user",
    )
    session.add(user)
    session.commit()

    retrieved = session.query(User).filter_by(username="adminuser").first()
    assert retrieved is not None
    assert retrieved.is_admin is True
    assert retrieved.additional_notes == "VIP user"


def test_user_has_timestamps(session):
    """User inherits TimeStampModel and has created/updated."""
    user = User(
        username="timestampuser",
        email="ts@example.com",
        password_hash="hash",
    )
    session.add(user)
    session.commit()

    retrieved = session.query(User).filter_by(username="timestampuser").first()
    assert retrieved.created is not None
    assert retrieved.updated is not None
