import stripe
from app.models.invoice import Invoice, InvoiceItem
from app.models.payments import Payment
from app.models.orders import OrderStatus, Order
from app.models.products import ProductVariant
from app.extensions import db


def test_webhook_invalid_payload(client, monkeypatch):
    """
    monkeypatch/mock modules and environments;
    safely set/delete an attribute, dictionary item or environment variable,
    or modify sys.path for importing
    monkeypatch uses helper methods
    """

    def mock_construct_event(*args, **kwargs):
        raise ValueError("Invalid payload")

    # patch the function or property
    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        mock_construct_event,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"invalid payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 400


def test_webhook_invalid_signature(client, monkeypatch):
    def mock_construct_event(*args, **kwargs):
        raise stripe.error.SignatureVerificationError(
            "Invalid signature",
            "test-signature",
        )

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        mock_construct_event,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "invalid-signature"},
    )

    assert response.status_code == 400


def test_webhook_missing_session_id(client, monkeypatch):
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {
                    "order_id": "1",
                },
                "payment_intent": "pi_test",
            }
        },
    }

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda *args, **kwargs: event,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "missing_session_id"}


def test_webhook_missing_order_id(client, monkeypatch):
    # hardcode values for unittests
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "payment_intent": "pi_test",
                "metadata": {},
            }
        },
    }

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda *args, **kwargs: event,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "missing_order_id"}


def test_webhook_unknown_order(client, monkeypatch):
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_unknown",
                "payment_intent": "pi_test",
                "currency": "mxn",
                "metadata": {
                    "order_id": "999999",
                },
            }
        },
    }

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda *args, **kwargs: event,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "order_not_found"}


def test_webhook_already_processed(client, paid_order, monkeypatch):
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": paid_order.stripe_session_id,
                "payment_intent": "pi_test_paid",
                "currency": "usd",
                "metadata": {
                    "order_id": str(paid_order.id),
                },
            }
        },
    }

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda *args, **kwargs: event,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


def test_webhook_insufficient_stock(
    client,
    order_with_inventory,
    monkeypatch,
):
    order, variant = order_with_inventory

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": order.stripe_session_id,
                "payment_intent": "pi_test_inventory",
                "currency": "mxn",
                "metadata": {
                    "order_id": str(order.id),
                },
            }
        },
    }

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda *args, **kwargs: event,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 409
    assert response.get_json() == {"error": "Insufficient stock"}

    assert variant.stock_quantity == 1


def test_webhook_valid_event(client, session, successful_order, monkeypatch):
    order, variant = successful_order

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": order.stripe_session_id,
                "payment_intent": "pi_test_success",
                "currency": "mxn",
                "metadata": {
                    "order_id": str(order.id),
                },
            }
        },
    }

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda *args, **kwargs: event,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"success": True}
    # text fixture has its own db.session and own transaction/session handling
    session.expire_all()

    assert order.status == OrderStatus.PAID
    assert order.stripe_payment_intent_id == "pi_test_success"

    assert variant.stock_quantity == 3

    invoice = session.query(Invoice).filter_by(order_id=order.id).one()

    assert invoice.status.value == "paid"
    assert invoice.customer_id == order.customer_id
    assert invoice.total_amount == order.total_amount
    assert invoice.currency == "mxn"

    invoice_item = session.query(InvoiceItem).filter_by(invoice_id=invoice.id).one()

    assert invoice_item.product_id == order.items[0].product_id
    assert invoice_item.quantity == order.items[0].quantity
    assert invoice_item.unit_price == order.items[0].unit_price

    payment = session.query(Payment).filter_by(invoice_id=invoice.id).one()

    assert payment.payment_amount == order.total_amount
    assert payment.payment_reference == "pi_test_success"
    assert payment.payment_method == "card"


def test_webhook_idempotency(
    client,
    session,
    successful_order,
    monkeypatch,
):
    order, variant = successful_order

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": order.stripe_session_id,
                "payment_intent": "pi_test_idempotency",
                "currency": "mxn",
                "metadata": {
                    "order_id": str(order.id),
                },
            }
        },
    }

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda *args, **kwargs: event,
    )

    # First webhook
    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"success": True}

    session.expire_all()

    first_invoice = session.query(Invoice).filter_by(order_id=order.id).one()

    first_payment = session.query(Payment).filter_by(invoice_id=first_invoice.id).one()

    assert variant.stock_quantity == 3

    # Same webhook again
    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}

    session.expire_all()

    # No second invoice
    invoices = session.query(Invoice).filter_by(order_id=order.id).all()

    assert len(invoices) == 1
    assert invoices[0].id == first_invoice.id

    # No second payment
    payments = session.query(Payment).filter_by(invoice_id=first_invoice.id).all()

    assert len(payments) == 1
    assert payments[0].id == first_payment.id

    # Inventory was not decremented again
    assert variant.stock_quantity == 3


def test_webhook_rollback(
    client,
    session,
    successful_order,
    monkeypatch,
):
    """
    make payment creation fail after;
    decremented inventory,
    created the invoice,
    created invoiceitems
    """
    order, variant = successful_order

    original_stock = variant.stock_quantity

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": order.stripe_session_id,
                "payment_intent": "pi_test_rollback",
                "currency": "mxn",
                "metadata": {
                    "order_id": str(order.id),
                },
            }
        },
    }

    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda *args, **kwargs: event,
    )

    def failing_payment(*args, **kwargs):
        raise RuntimeError("Simulated payment failure")

    monkeypatch.setattr(
        "app.routes.stripe.Payment",
        failing_payment,
    )

    response = client.post(
        "/api/admin/webhook",
        data=b"test payload",
        headers={"Stripe-Signature": "test-signature"},
    )

    assert response.status_code == 500
    assert response.get_json() == {"error": "internal_server_error"}

    db.session.expire_all()

    order_after = db.session.query(Order).filter_by(id=order.id).one()

    variant_after = db.session.query(ProductVariant).filter_by(id=variant.id).one()

    assert order_after.status == OrderStatus.PENDING
    assert variant_after.stock_quantity == original_stock

    invoice = db.session.query(Invoice).filter_by(order_id=order.id).first()

    assert invoice is None

    payment = (
        db.session.query(Payment)
        .filter_by(payment_reference="pi_test_rollback")
        .first()
    )

    assert payment is None
