# file: tests/test_checkout.py
# descr: real cart and real cart item, mock only stripe.checkout.session.create, call the http endpoint, inspect the resulting order


from decimal import Decimal
from unittest.mock import MagicMock
from app.models.customers import CustomerDeliveryZone
from app.models.cart import Cart, CartItem
from app.models.orders import Order, OrderStatus


def test_checkout_success(client, cart_product_variant, session, monkeypatch):
    """
    create the cart and cartitem
    """
    customer, product, variant = cart_product_variant

    delivery_zone = CustomerDeliveryZone(
        customer_id=customer.id,
        zip_code="45000",
    )
    session.add(delivery_zone)

    cart = Cart(
        cart_token="checkout-test-token",
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

    session.add(cart_item)
    session.commit()

    stripe_session = MagicMock()
    stripe_session.id = "cs_test_checkout_123"
    stripe_session.url = "https://checkout.stripe.com/test"

    stripe_create = MagicMock(return_value=stripe_session)

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

    assert response.status_code == 200

    data = response.get_json()

    assert data["checkout_url"] == stripe_session.url

    order = Order.query.filter_by(cart_id=cart.id).first()

    assert order is not None
    assert order.status == OrderStatus.PENDING
    assert order.customer_id == customer.id
    assert order.total_amount == Decimal("50.00")
    assert order.stripe_session_id == stripe_session.id

    assert order.shipping_address_1 == "Av. Example 123"
    assert order.shipping_address_2 is None
    assert order.shipping_country == "Mexico"
    assert order.shipping_city == "Zapopan"
    assert order.shipping_zip_code == "45000"
    assert order.shipping_state == "Jalisco"

    assert len(order.items) == 1

    order_item = order.items[0]

    assert order_item.product_id == product.id
    assert order_item.product_variant_id == variant.id
    assert order_item.quantity == 2
    assert order_item.unit_price == Decimal("25.00")

    stripe_create.assert_called_once()

    stripe_kwargs = stripe_create.call_args.kwargs

    assert stripe_kwargs["mode"] == "payment"
    assert stripe_kwargs["metadata"] == {
        "order_id": str(order.id),
    }

    assert stripe_kwargs["line_items"] == [
        {
            "price_data": {
                "currency": "mxn",
                "product_data": {
                    "name": product.name,
                },
                "unit_amount": 2500,
            },
            "quantity": 2,
        }
    ]


def test_checkout_cart_not_found(client):
    response = client.post(
        "/api/checkout",
        json={
            "cart_token": "unknown-cart-token",
            "shipping_address_1": "Av. Example 123",
            "shipping_address_2": None,
            "shipping_country": "Mexico",
            "shipping_city": "Zapopan",
            "shipping_zip_code": "45000",
            "shipping_state": "Jalisco",
        },
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Cart not found"


def test_checkout_empty_cart(client, cart_product_variant, session):
    customer, _, _ = cart_product_variant

    cart = Cart(
        cart_token="empty-checkout-test-token",
        customer_id=customer.id,
        total_amount=Decimal("0.00"),
    )

    session.add(cart)
    session.commit()

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

    assert data["error"] == "Cart is empty"


def test_checkout_already_started(client, cart_product_variant, session):
    """
    Verify one order per cart policy;
    cart.order is not none
    """
    customer, product, variant = cart_product_variant

    cart = Cart(
        cart_token="existing-order-test-token",
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

    order = Order(
        cart=cart,
        customer_id=customer.id,
        status=OrderStatus.PENDING,
        total_amount=Decimal("50.00"),
        shipping_address_1="Av. Example 123",
        shipping_address_2=None,
        shipping_country="Mexico",
        shipping_city="Zapopan",
        shipping_zip_code="45000",
        shipping_state="Jalisco",
    )

    session.add_all([cart_item, order])
    session.commit()

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

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Checkout already started for this cart"


def test_checkout_missing_cart_token(client):
    response = client.post(
        "/api/checkout",
        json={
            "shipping_address_1": "Av. Example 123",
            "shipping_country": "Mexico",
            "shipping_city": "Zapopan",
            "shipping_zip_code": "45000",
            "shipping_state": "Jalisco",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "cart_token is required"


def test_checkout_missing_shipping_field(client):
    response = client.post(
        "/api/checkout",
        json={
            "cart_token": "checkout-test-token",
            "shipping_address_1": "Av. Example 123",
            "shipping_country": "Mexico",
            "shipping_city": "Zapopan",
            "shipping_state": "Jalisco",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "shipping_zip_code is required"


def test_checkout_stripe_creation_failed(
    client,
    cart_product_variant,
    session,
    monkeypatch,
):
    customer, product, variant = cart_product_variant

    cart = Cart(
        cart_token="stripe-failure-test-token",
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

    delivery_zone = CustomerDeliveryZone(
        customer_id=customer.id,
        zip_code="45000",
    )

    session.add_all([delivery_zone, cart_item])
    session.commit()

    def raise_stripe_error(**kwargs):
        raise Exception("Stripe Checkout failed")

    monkeypatch.setattr(
        "app.routes.checkout.stripe.checkout.Session.create",
        raise_stripe_error,
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

    assert response.status_code == 500

    data = response.get_json()

    assert data["error"] == "Checkout failed. Please try again later."

    order = Order.query.filter_by(cart_id=cart.id).first()

    assert order is None
