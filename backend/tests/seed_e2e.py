# file: tests/seed_e2e.py
# descr: seed e2e backend in containers for Playwright

from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models.customers import Customer, CustomerDeliveryZone
from app.models.products import Product, ProductVariant


def seed() -> None:
    """Create the data required by the E2E test suite."""
    customer = Customer(
        customer_id="e2e-customer",
        customer_name="E2E Test Customer",
        customer_email="e2e@example.test",
    )

    delivery_zone = CustomerDeliveryZone(
        customer=customer,
        zip_code="45000",
    )

    product = Product(
        product_id="e2e-product",
        name="cart-test-product",
        customer=customer,
        brand="E2E",
        category="Test",
        description="Product used by Playwright E2E tests.",
    )

    variant = ProductVariant(
        product=product,
        price=Decimal("29.99"),
        stock_quantity=10,
        sku="E2E-CART-001",
    )

    db.session.add_all([customer, delivery_zone, product, variant])
    db.session.commit()


def main() -> None:
    """Create the application context and seed the E2E database."""
    app = create_app()
    with app.app_context():
        seed()


if __name__ == "__main__":
    main()
