from decimal import Decimal
from unittest.mock import MagicMock

from app.models.cart import Cart, CartItem
from app.models.customers import CustomerDeliveryZone
from app.models.orders import Order, OrderStatus


def test_get_order_returns_shipping_address(client, paid_order):
    response = client.get(
        f"/api/orders/{paid_order.id}",
        headers={"X-Cart-Token": paid_order.cart.cart_token},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == paid_order.id
    assert data["status"] == OrderStatus.PAID.value
    assert data["shipping_zip_code"] == "12345"
    assert data["shipping_address_1"] == "123 Test Street"


def test_get_order_requires_cart_token(client, paid_order):
    response = client.get(f"/api/orders/{paid_order.id}")

    assert response.status_code == 401
    assert response.get_json()["error"] == "X-Cart-Token header is required"


def test_get_unknown_order_returns_not_found(client, paid_order):
    response = client.get(
        "/api/orders/999999",
        headers={"X-Cart-Token": paid_order.cart.cart_token},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Order not found"


def test_get_order_rejects_another_cart_token(client, paid_order):
    response = client.get(
        f"/api/orders/{paid_order.id}",
        headers={"X-Cart-Token": "unrelated-cart-token"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Order not found"


def test_checkout_order_zip_is_read_through_api(
    client, cart_product_variant, session, monkeypatch
):
    customer, product, variant = cart_product_variant
    session.add(CustomerDeliveryZone(customer_id=customer.id, zip_code="45000"))

    cart = Cart(
        cart_token="order-read-checkout-token",
        customer_id=customer.id,
        total_amount=Decimal("50.00"),
    )
    session.add(
        CartItem(
            cart=cart,
            product_id=product.id,
            product_variant_id=variant.id,
            quantity=2,
            unit_price=Decimal("25.00"),
        )
    )
    session.commit()

    stripe_session = MagicMock()
    stripe_session.id = "cs_test_order_read_123"
    stripe_session.url = "https://checkout.stripe.com/test"
    monkeypatch.setattr(
        "app.routes.checkout.stripe.checkout.Session.create",
        MagicMock(return_value=stripe_session),
    )

    checkout_response = client.post(
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

    assert checkout_response.status_code == 200
    checkout_data = checkout_response.get_json()
    assert checkout_data["checkout_url"] == stripe_session.url
    assert isinstance(checkout_data["order_id"], int)

    order_response = client.get(
        f"/api/orders/{checkout_data['order_id']}",
        headers={"X-Cart-Token": cart.cart_token},
    )

    assert order_response.status_code == 200
    assert order_response.get_json()["shipping_zip_code"] == "45000"
