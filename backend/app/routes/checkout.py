# file: checkout.py
# descr:

import stripe
from flask import Blueprint, current_app, jsonify, request, current_app

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

    if cart.order is not None:
        return jsonify({"error": "Checkout already started for this cart"}), 409

    sellers = {item.product.customer for item in cart.items}

    for seller in sellers:
        if not customer_delivers_to_zip(seller.id, shipping_zip_code):
            return (
                jsonify({"error": "Seller does not deliver to the provided ZIP code"}),
                400,
            )

    try:
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
            success_url=current_app.config["STRIPE_SUCCESS_URL"],
            cancel_url=current_app.config["STRIPE_CANCEL_URL"],
        )

        order.stripe_session_id = session.id

        db.session.commit()

        return jsonify({"checkout_url": session.url}), 200

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Checkout failed")
        return jsonify({"error": "Checkout failed. Please try again later."}), 500
