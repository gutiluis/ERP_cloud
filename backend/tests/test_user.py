"""
file: tests/test_user.py
descr:
Tests for the User model using pytest and the test DB (e.g. Docker).

- Use the session fixture; do not use db.session directly in tests.
- Ensure tests/ has __init__.py so it is recognized as a package.
"""

from app.models.user import User


def test_create_user(session):
    """Create a user with required fields and check defaults."""
    user = User(
        email="testuser@example.com",
    )
    session.add(user)
    session.commit()

    retrieved = session.query(User).filter_by(email="testuser@example.com").first()
    assert retrieved is not None
    assert retrieved.email == "testuser@example.com"
    assert retrieved.additional_notes is None


def test_create_user_with_optionals(session):
    """Create a user with optional fields set."""
    user = User(
        email="admin@example.com",
        additional_notes="some notes",
    )
    session.add(user)
    session.commit()

    retrieved = session.query(User).filter_by(additional_notes="some notes").first()
    assert retrieved is not None
    assert retrieved.additional_notes == "some notes"


def test_user_has_timestamps(session):
    """User inherits TimeStampModel and has created/updated."""
    user = User(
        email="ts@example.com",
    )
    session.add(user)
    session.commit()

    retrieved = session.query(User).filter_by(email="ts@example.com").first()
    assert retrieved.created is not None
    assert retrieved.updated is not None
