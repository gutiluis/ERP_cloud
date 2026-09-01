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
from decimal import Decimal
from app.models.products import Product, ProductVariant
from app.models.orders import Order, OrderItem, OrderStatus
from app.models.admin_user import AdminUser
from app.models.cart import Cart
from app.models.customers import Customer


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ["TEST_DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STRIPE_WEBHOOK_SECRET = "test_stripe.pyPassword"


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)

    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def db_(app):
    """
    Make db clean before each test
    """
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope="function")
def session(db_):
    yield db_.session
    db_.session.rollback()
    db_.session.remove()


@pytest.fixture
def client(app, db_):
    return app.test_client()


@pytest.fixture
def paid_order(session):
    admin = AdminUser(
        admin_id="admin_test_001",
        username="stripe_test_admin",
        email="stripe_test@example.com",
        password_hash="test-password-hash",
    )

    customer = Customer(
        customer_id="customer_test_001",
        customer_name="Stripe Test Customer",
        customer_email="customer_test@example.com",
    )

    session.add_all([admin, customer])
    session.flush()

    cart = Cart(
        cart_token="stripe_test_cart_001",
        customer_id=customer.id,
        total_amount=100.00,
    )

    session.add(cart)
    session.flush()

    order = Order(
        stripe_session_id="cs_test_paid",
        status=OrderStatus.PAID,
        total_amount=100.00,
        operator_admin_id=admin.id,
        customer_id=customer.id,
        cart_id=cart.id,
        shipping_address_1="123 Test Street",
        shipping_address_2=None,
        shipping_country="US",
        shipping_city="Test City",
        shipping_zip_code="12345",
        shipping_state="Test State",
    )

    session.add(order)
    session.flush()

    return order


@pytest.fixture
def order_with_inventory(session):
    admin = AdminUser(
        admin_id="admin_inventory_001",
        username="stripe_inventory_admin",
        email="stripe_inventory@example.com",
        password_hash="test-password-hash",
    )

    customer = Customer(
        customer_id="customer_inventory_001",
        customer_name="Stripe Inventory Customer",
        customer_email="stripe_inventory@example.com",
    )

    session.add_all([admin, customer])
    session.flush()

    cart = Cart(
        cart_token="stripe_inventory_cart_001",
        customer_id=customer.id,
        total_amount=Decimal("20.00"),
    )

    product = Product(
        product_id="product_inventory_001",
        product_name="Stripe Test Product",
        customer_id=customer.customer_id,
        brand="Test Brand",
        category="Test Category",
        description="Stripe inventory test product",
    )

    session.add_all([cart, product])
    session.flush()

    variant = ProductVariant(
        product_id=product.id,
        is_active=True,
        price=Decimal("10.00"),
        stock_quantity=1,
        sku="STRIPE-TEST-SKU-001",
    )

    session.add(variant)
    session.flush()

    order = Order(
        stripe_session_id="cs_test_inventory",
        status=OrderStatus.PENDING,
        total_amount=Decimal("20.00"),
        operator_admin_id=admin.id,
        customer_id=customer.id,
        cart_id=cart.id,
        shipping_address_1="123 Test Street",
        shipping_address_2=None,
        shipping_country="US",
        shipping_city="Test City",
        shipping_zip_code="12345",
        shipping_state="Test State",
    )

    session.add(order)
    session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_variant_id=variant.id,
        quantity=2,
        unit_price=Decimal("10.00"),
    )

    session.add(order_item)
    session.flush()

    return order, variant


@pytest.fixture
def successful_order(session):
    admin = AdminUser(
        admin_id="admin_success_001",
        username="stripe_success_admin",
        email="stripe_success@example.com",
        password_hash="test-password-hash",
    )

    customer = Customer(
        customer_id="customer_success_001",
        customer_name="Stripe Success Customer",
        customer_email="stripe_success@example.com",
    )

    session.add_all([admin, customer])
    session.flush()

    cart = Cart(
        cart_token="stripe_success_cart_001",
        customer_id=customer.id,
        total_amount=Decimal("20.00"),
    )

    product = Product(
        product_id="product_success_001",
        product_name="Stripe Success Product",
        customer_id=customer.customer_id,
        brand="Test Brand",
        category="Test Category",
        description="Stripe successful webhook test product",
    )

    session.add_all([cart, product])
    session.flush()

    variant = ProductVariant(
        product_id=product.id,
        is_active=True,
        price=Decimal("10.00"),
        stock_quantity=5,
        sku="STRIPE-SUCCESS-SKU-001",
    )

    session.add(variant)
    session.flush()

    order = Order(
        stripe_session_id="cs_test_success",
        status=OrderStatus.PENDING,
        total_amount=Decimal("20.00"),
        operator_admin_id=admin.id,
        customer_id=customer.id,
        cart_id=cart.id,
        shipping_address_1="123 Test Street",
        shipping_address_2=None,
        shipping_country="US",
        shipping_city="Test City",
        shipping_zip_code="12345",
        shipping_state="Test State",
    )

    session.add(order)
    session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_variant_id=variant.id,
        quantity=2,
        unit_price=Decimal("10.00"),
    )

    session.add(order_item)
    session.commit()

    return order, variant
