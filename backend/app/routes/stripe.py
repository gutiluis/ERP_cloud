#!/usr/bin/env python3


"""
# file: /app/routes/stripe.py

# descr: make a new invoice from the stripe payment and do not make the routes/invoice.py route
# listen for events from stripe on webhook endpoint so integration can automatically trigger reactions
# event object with json payload
# webhook events help respond to asynchronous events, such as when a customer's bank confirms a payment, a customer disputes a charge, or a recurring payment succeeds

# check SSL for debugging
# cloudflare offers free ssl certificates. if tls has ssl which is old
#
# idempotency guarantees that no more than one object is created
"""


import stripe
from stripe.error import SignatureVerificationError
from flask import Blueprint, request, current_app, abort, redirect
from app import db
from app.extensions import login_required, current_user, Decimal
from app.models.invoice import Invoice
from app.models.orders import Order, OrterItem
from app.models.cart import Cart
from app import config

stripe_bp = Blueprint(
    "stripe",
    __name__,
    url_prefix="/api/admin"
)


@stripe_bp.route("/checkout", methods=["POST"])
#@login_required
def checkout():
    """
    load cart before checkout
    Stripe checkout session creation for webhook. webhook needs order and other models
        """
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart:
        return {"error": "Cart not found"}, 404

    if not cart.items:
        return {"error": "Cart is empty"}, 400

    order = Order(
        user_id=current_user.id,
        status="pending",
        total_amount=cart.total_amount
    )
    db.session.add(order)
    db.session.flush() # gets order.id before commit
    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.price
        )
        db.session.add(order_item)
    db.session.commit()

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.product.name,
                    },
                    "unit_amount": int(item.price * 100),
                },
                "quantity": item.quantity,
            }
            for item in cart.items
        ],
        metadata={
            "order_id": str(order.id)
        },
        success_url="https://yourapp.com/success",
        cancel_url="https://yourapp.com/cart",
    )

    return {"checkout_url": session.url}




# Idempotency-Key header
# Stripe-Should-Retry # header for idempotency
# change to https after
# create webhook endpoint handler to receive event data post requests
@stripe_bp.route("/webhook", methods=["POST"])
def webhook():
    # all event share same structure except data property
    # event body
    payload = request.data
    # signature parameter for constructEvent()
    # event payload verification. with endpoint's secret verification in the try statement
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            # import config.py
            # endpoint secret associated parameter for construct_event
            current_app.config["STRIPE_WEBHOOK_SECRET"]
        )
    except ValueError as e:
        # 400 bad request
        print("[ERROR] INVALID PAYLOAD", e)
        abort(400)
        # verify webhook authenticity
    except stripe.error.SignatureVerificationError as e:
        print("INVALID SIGNATURE:", e)
        abort(400)


    if event["type"] != "checkout.session.completed":
        return {"ignored": True}, 200

    session = event["data"]["object"]

    print("EVENT:", event["type"])
    print("SESSION ID:", session.get("id"))
    print("METADATA:", session.get("metadata"))

    
    stripe_session_id = session.get("id")

    if not stripe_session_id:
        return {"error": "missing_session_id"}, 400
    # web api design principle as the ability to apply the same operation multiple times without changing the result beyond the first try
    # exponential backoff and random jitter
    # put and delete http methods are idempotent
    # idempotency check. # from invoice model
    # not from any model
    order_id = session.get("metadata", {}).get("order_id")


    if not order_id:
        return {"error": "missing_order_id"}, 400

    order = (
        db.session.query(Order)
        .filter_by(stripe_session_id=stripe_session_id)
        .first()
    )


    # needs a session
    if not order:
        print("LOOKUP FAILED")
        print("stripe_session_id", stripe_session_id)
        print("order_id metadata:", order_id)
        return {"error": "order_not_found"}, 404

    if order.status == "paid":
        return {"ok": True}, 200


    existing_invoice = (
        db.session.query(Invoice)
        .filter_by(order_id=order.id)
        .first()
    )
    if existing_invoice:
        return {"ok": True}, 200

    payment = Payment(
        order_id=order.id,
        customer_id=order.customer_id,
        stripe_payment_intent_id=session.get("payment_intent"),
        status="paid",
        amount=order.total_amount,
        currency=session.get("currency"),
    )
    db.session.add(payment)

    invoice=Invoice(
        order_id=order.id,
        status="paid",
        currency=session.get("currency"),
        customer_id=order.customer_id,
    )

    db.session.add(invoice)

    for copy_item_from_order in order.items:
        invoice.items.append(
            InvoiceItem(
                product_id=copy_item_from_order.product_id,
                quantity=copy_item_from_order.quantity,
                unit_price=copy_item_from_order.unit_price,
            )
        )

    order.status = "paid"

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return {"success": True}, 200
