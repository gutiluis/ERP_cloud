# file: checkout.py
# descr: verify stripe payment

import time

import stripe
from flask import Blueprint, jsonify, request, current_app

from app import db
from app.models.cart import Cart
from app.models.orders import Order, OrderItem
from app.services.delivery import customer_delivers_to_zip


checkout_bp = Blueprint("checkout", __name__, url_prefix="/api")


@checkout_bp.route("/checkout", methods=["POST"])
def checkout():
    """
    Interactive view for the frontend
    """
    data = request.get_json(silent=True) or {}
    # /frontend/src/api/checkout.js
    cart_token = data.get("cart_token")
    shipping_address_1 = data.get("shipping_address_1")
    shipping_address_2 = data.get("shipping_address_2")
    shipping_country = data.get("shipping_country")
    shipping_city = data.get("shipping_city")
    shipping_zip_code = data.get("shipping_zip_code")
    shipping_state = data.get("shipping_state")

    if not isinstance(cart_token, str) or not cart_token:
        return jsonify({"error": "cart_token is required"}), 400

    if not isinstance(shipping_address_1, str) or not shipping_address_1:
        return jsonify({"error": "shipping_address_1 is required"}), 400

    if not isinstance(shipping_country, str) or not shipping_country:
        return jsonify({"error": "shipping_country is required"}), 400

    if not isinstance(shipping_city, str) or not shipping_city:
        return jsonify({"error": "shipping_city is required"}), 400

    if not isinstance(shipping_zip_code, str) or not shipping_zip_code:
        return jsonify({"error": "shipping_zip_code is required"}), 400

    if not isinstance(shipping_state, str) or not shipping_state:
        return jsonify({"error": "shipping_state is required"}), 400

    cart = (
        db.session.execute(db.select(Cart).where(Cart.cart_token == cart_token))
        .scalars()
        .first()
    )
    # existing cart tests
    if cart is None:
        return jsonify({"error": "Cart not found"}), 404

    if not cart.items:
        return jsonify({"error": "Cart is empty"}), 400

    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    order = cart.order
    if order is not None:
        if order.status.value != "pending":
            return jsonify({"error": "This order cannot be checked out again"}), 409

        if not order.stripe_session_id:
            return jsonify({"error": "Checkout already started for this cart"}), 409

        try:
            existing_session = stripe.checkout.Session.retrieve(order.stripe_session_id)
        except stripe.StripeError:
            current_app.logger.exception("Unable to retrieve existing checkout")
            return jsonify({"error": "Unable to verify existing checkout"}), 502

        if (
            existing_session.payment_status == "paid"
            or existing_session.status == "complete"
        ):
            return jsonify({"error": "Checkout has already been completed"}), 409

        if existing_session.status == "open":
            return jsonify(
                {
                    "checkout_url": existing_session.url,
                    "order_id": order.id,
                }
            ), 200

        if existing_session.status != "expired":
            return jsonify({"error": "Existing checkout cannot be restarted"}), 409

    sellers = {item.product.customer for item in cart.items}

    for seller in sellers:
        if not customer_delivers_to_zip(seller.id, shipping_zip_code):
            return (
                jsonify({"error": "Seller does not deliver to the provided ZIP code"}),
                400,
            )

    try:
        if order is None:
            order = Order(
                cart=cart,
                customer_id=cart.customer_id,
                status="pending",
                total_amount=cart.total_amount,
                shipping_address_1=shipping_address_1,
                shipping_address_2=shipping_address_2,
                shipping_country=shipping_country,
                shipping_city=shipping_city,
                shipping_zip_code=shipping_zip_code,
                shipping_state=shipping_state,
            )
            db.session.add(order)
            db.session.flush()
        else:
            order.total_amount = cart.total_amount
            order.shipping_address_1 = shipping_address_1
            order.shipping_address_2 = shipping_address_2
            order.shipping_country = shipping_country
            order.shipping_city = shipping_city
            order.shipping_zip_code = shipping_zip_code
            order.shipping_state = shipping_state
            order.items.clear()

        for item in cart.items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    product_variant_id=item.product_variant_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
            )

        session = stripe.checkout.Session.create(
            mode="payment",
            expires_at=int(time.time()) + 30 * 60,
            line_items=[
                {
                    "price_data": {
                        "currency": "mxn",
                        "product_data": {
                            "name": item.product.name,
                        },
                        "unit_amount": int(item.unit_price * 100),
                    },
                    "quantity": item.quantity,
                }
                for item in cart.items
            ],
            metadata={"order_id": str(order.id)},
            success_url=(
                f"{current_app.config['STRIPE_SUCCESS_URL']}"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=(
                f"{current_app.config['STRIPE_CANCEL_URL']}"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
        )

        order.stripe_session_id = session.id

        db.session.commit()

        return jsonify({"checkout_url": session.url, "order_id": order.id}), 200

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Checkout failed")
        return jsonify({"error": "Checkout failed. Please try again later."}), 500


@checkout_bp.post("/checkout/cancel")
def cancel_checkout():
    """Expire an open Stripe Checkout Session belonging to the supplied cart."""
    data = request.get_json(silent=True) or {}
    cart_token = data.get("cart_token")
    session_id = data.get("session_id")

    if not isinstance(cart_token, str) or not cart_token:
        return jsonify({"error": "cart_token is required"}), 400
    if not isinstance(session_id, str) or not session_id:
        return jsonify({"error": "session_id is required"}), 400

    order = db.session.execute(
        db.select(Order).where(Order.stripe_session_id == session_id)
    ).scalar_one_or_none()

    if order is None or order.cart.cart_token != cart_token:
        return jsonify({"error": "Checkout session not found"}), 404

    try:
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
        session = stripe.checkout.Session.retrieve(session_id)

        if session.status == "open":
            stripe.checkout.Session.expire(session_id)
        elif session.status == "complete":
            return jsonify({"error": "Checkout has already been completed"}), 409

        return jsonify({"status": "canceled"}), 200
    except stripe.StripeError:
        current_app.logger.exception("Failed to cancel checkout")
        return jsonify({"error": "Unable to cancel checkout"}), 502


@checkout_bp.get("/orders/payment-status")
def get_payment_status():
    """Explicit synchronization, Idempotent transition, Real verification, Ownership check"""
    session_id = request.args.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    order = db.session.execute(
        db.select(Order).where(Order.stripe_session_id == session_id)
    ).scalar_one_or_none()

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    try:
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        current_app.logger.exception("Stripe payment verification failed")
        return jsonify({"error": "Unable to verify payment"}), 502

    if session.metadata["order_id"] != str(order.id):
        return jsonify({"error": "Checkout session does not match order"}), 400

    status_type = type(order.status)
    pending_status = getattr(status_type, "PENDING", "PENDING")
    paid_status = getattr(status_type, "PAID", "PAID")

    if session.payment_status == "paid":
        try:
            db.session.execute(
                db.update(Order)
                .where(
                    Order.id == order.id,
                    Order.status == pending_status,
                )
                .values(status=paid_status)
            )
            db.session.commit()
            db.session.refresh(order)
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Failed to update order payment status")
            return jsonify({"error": "Unable to update order status"}), 500

    status = order.status.value if hasattr(order.status, "value") else order.status

    return jsonify({"status": str(status).lower()}), 200
