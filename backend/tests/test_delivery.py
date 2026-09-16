# file: test_delivery.py
# descr: customer's delivery test

from unittest.mock import MagicMock
from decimal import Decimal
from app.models.cart import Cart, CartItem
from app.models import Customer, CustomerDeliveryZone
from app.models.orders import Order
from app.services.delivery import customer_delivers_to_zip


def test_customer_delivers_to_zip(session):
    """Return true when a customer covers the requested ZIP code."""
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

    assert customer_delivers_to_zip(customer.id, "75001") is True


def test_customer_does_not_deliver_to_zip(session):
    """Return false when a customer does not cover the requested ZIP code."""
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

    assert customer_delivers_to_zip(customer.id, "75002") is False


def test_customer_delivery_zones_are_independent(session):
    """Return coverage only for the requested customer."""
    first_customer = Customer(
        customer_id="First Customer id",
        customer_name="First customer name",
        customer_address="first_address",
    )
    second_customer = Customer(
        customer_id="Second Customer id",
        customer_name="Second customer name",
        customer_address="second_address",
    )

    session.add_all([first_customer, second_customer])
    session.commit()

    delivery_zone = CustomerDeliveryZone(
        customer_id=first_customer.id,
        zip_code="75001",
    )
    session.add(delivery_zone)
    session.commit()

    assert customer_delivers_to_zip(first_customer.id, "75001") is True
    assert customer_delivers_to_zip(second_customer.id, "75001") is False


def test_checkout_rejects_unsupported_delivery_zip(
    client,
    cart_product_variant,
    session,
    monkeypatch,
):
    customer, product, variant = cart_product_variant

    delivery_zone = CustomerDeliveryZone(
        customer_id=customer.id,
        zip_code="44100",
    )

    cart = Cart(
        cart_token="checkout-delivery-test-token",
        customer_id=customer.id,
        total_amount=Decimal("50.00"),
    )

    cart_item = CartItem(
        cart=cart,
        product_id=product.id,
        product_variant_id=variant.id,
        quantity=2,
        unit_price=Decimal("25.00"),
    )

    session.add_all([delivery_zone, cart_item])
    session.commit()

    stripe_create = MagicMock()

    monkeypatch.setattr(
        "app.routes.checkout.stripe.checkout.Session.create",
        stripe_create,
    )

    response = client.post(
        "/api/checkout",
        json={
            "cart_token": cart.cart_token,
            "shipping_address_1": "Av. Example 123",
            "shipping_address_2": None,
            "shipping_country": "Mexico",
            "shipping_city": "Zapopan",
            "shipping_zip_code": "45000",
            "shipping_state": "Jalisco",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == ("Seller does not deliver to the provided ZIP code")

    order = Order.query.filter_by(cart_id=cart.id).first()

    assert order is None

    stripe_create.assert_not_called()
