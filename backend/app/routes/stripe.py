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
from app import db
from app.models.cart import Cart
from app.models.invoice import Invoice, InvoiceItem
from app.models.orders import Order, OrderItem
from app.models.payments import Payment
from flask import Blueprint, abort, current_app, request

stripe_bp = Blueprint("stripe", __name__, url_prefix="/api/admin")


@stripe_bp.route("/checkout", methods=["POST"])
# @login_required # remove for testing
def checkout():
    """
    cart is created/managed by react frontend
    order is created by flask backend. the order is made by the function and needs to be constructed before the webhook
    load cart before checkout with order
    Stripe checkout session creation for webhook. webhook needs order and other models
    """
    data = request.get_json()
    cart_id = data["cart_id"]
    # the cart is a buyer session
    cart = Cart.query.get(cart_id)  # load from cart model

    if not cart:
        return {"error": "Cart not found"}, 404

    if not cart.items:
        return {"error": "Cart is empty"}, 400

    existing_order = Order.query.filter_by(cart_id=cart.id, status="pending").first()
    if existing_order:
        return {"error", "Checkout already started for this cart"}, 409

    try:
        # cart and order products come from the customers model
        order = Order(
            customer_id=cart.customer_id,
            status="pending",
            total_amount=cart.total_amount,
        )
        db.session.add(order)
        db.session.flush()  # gets order.id before commit
        # add order items
        for item in cart.items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.price,
                )
            )

        # stripe checkout session create might raise an exception stop commitment
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
            metadata={"order_id": str(order.id)},
            success_url="https://yourapp.com/success",
            cancel_url="https://yourapp.com/cart",
        )
        order.stripe_session_id = session.id
        db.session.commit()

        return {"checkout_url": session.url}
    except Exception as err:
        db.session.rollback()
        current_app.logger.exception("Checkout Failed")
        return {"error", str(err)}, 500


# Stripe-Should-Retry # header for idempotency
# change to https after
# create webhook endpoint handler to receive event data post requests
@stripe_bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Process completed payments
    Idempotency check
    Listen for events to automatically trigger reactions
    Receive eventes at an https webhook endpoint
    load order, check if order already paid, check for an existing invoice and payment, create payment and invoice, copy invoice item, mark order as paid, commit
    inventory should be updated and tracked
    order made before stripe checkout
    """
    # all event share same structure except data property
    # event body
    print("[INFO] WEBHOOOK HIT")
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
            current_app.config["STRIPE_WEBHOOK_SECRET"],
        )
        print("EVENT TYPE:", event["type"])
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
    print("METADATA:", session.get("metadata"))  # no metadata

    stripe_session_id = session.get("id")
    payment_intent = session.get("payment_intent")
    order_id = session.get("metadata", {}).get("order_id")

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
        db.session.query(Order).filter_by(stripe_session_id=stripe_session_id).first()
    )

    # needs a session
    if not order:
        print("LOOKUP FAILED")
        print("stripe_session_id", stripe_session_id)
        print("order_id metadata:", order_id)
        return {"error": "order_not_found"}, 404

    if order.status == "paid":
        return {"ok": True}, 200

    # idempotency duplicate invoice
    existing_invoice = db.session.query(Invoice).filter_by(order_id=order.id).first()
    if existing_invoice:
        return {"ok": True}, 200

    try:
        for order_item in order.items:
            variant = order_item.product_variant

            if not variant.is_in_stock:
                db.session.rollback()
                return {"error", "Product is out of stock"}, 409

            if variant.stock_quantity < order_item.quantity:
                db.session.rollback()
                return {"error", "Insufficient stock"}, 409
        # reduce inventory
        for order_item in order.items:
            variant = order_item.product_variant
            variant.stock_quantity -= order_item.quantity

        # payment class instantiation
        payment = Payment(
            order_id=order.id,
            customer_id=order.customer_id,
            stripe_payment_intent_id=payment_intent,
            status="paid",
            amount=order.total_amount,
            currency=session.get("currency"),
        )
        db.session.add(payment)
        # invoice instantiation
        invoice = Invoice(
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
            return {"success": True}, 200
        except Exception:
            db.session.rollback()
            raise
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Stripe webhoook failed")
        return {"error": "internal_server_error"}, 500
