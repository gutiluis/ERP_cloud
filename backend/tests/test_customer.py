"""
Script to test the customer model using pytest and a testing db running in docker


fixture to reuse model setup inside every test also with a session

Make sure tests has __init__.py to be recognized as a package

never use db.session in test with a session fixture

"""

from app.models.customers import Customer, CustomerDeliveryZone
import pytest
from sqlalchemy.exc import IntegrityError


def test_create_customer(session):
    """Create a customer considering not nullable fields, index, max length in SQL"""
    customer = Customer(
        customer_id="Test Customer id",  # watching nullable=False
        customer_name="Test customer name",
        customer_address="test_address, country zip code",
    )
    session.add(customer)
    session.commit()

    retrieved = (
        session.query(Customer).filter_by(customer_id="Test Customer id").first()
    )
    assert retrieved is not None
    assert retrieved.customer_name == "Test customer name"
    assert retrieved.customer_address == "test_address, country zip code"


def test_create_customer_delivery_zone(session):
    """Create a delivery zone for a customer."""
    customer = Customer(
        customer_id="Test Customer id",
        customer_name="Test customer name",
        customer_address="test_address, country zip code",
    )
    session.add(customer)
    session.commit()

    delivery_zone = CustomerDeliveryZone(
        customer_id=customer.id,
        zip_code="75001",
    )
    session.add(delivery_zone)
    session.commit()

    retrieved = (
        session.query(CustomerDeliveryZone)
        .filter_by(customer_id=customer.id, zip_code="75001")
        .first()
    )

    assert retrieved is not None
    assert retrieved.customer_id == customer.id
    assert retrieved.zip_code == "75001"


def test_customer_delivery_zones_relationship(session):
    """Load a customer's delivery zones through the relationship."""
    customer = Customer(
        customer_id="Test Customer id",
        customer_name="Test customer name",
        customer_address="test_address, country zip code",
    )
    session.add(customer)
    session.commit()

    delivery_zone = CustomerDeliveryZone(
        customer_id=customer.id,
        zip_code="75001",
    )
    session.add(delivery_zone)
    session.commit()

    session.refresh(customer)

    assert len(customer.delivery_zones) == 1
    assert customer.delivery_zones[0].zip_code == "75001"


def test_customer_delivery_zone_zip_code_is_unique(session):
    """Prevent duplicate delivery zones for the same customer."""
    customer = Customer(
        customer_id="Test Customer id",
        customer_name="Test customer name",
        customer_address="test_address, country zip code",
    )
    session.add(customer)
    session.commit()

    first_zone = CustomerDeliveryZone(
        customer_id=customer.id,
        zip_code="75001",
    )
    duplicate_zone = CustomerDeliveryZone(
        customer_id=customer.id,
        zip_code="75001",
    )

    session.add(first_zone)
    session.commit()

    session.add(duplicate_zone)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
