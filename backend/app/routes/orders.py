"""Read orders owned by a guest checkout token."""

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.orders import Order

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.get("/<int:order_id>")
def get_order(order_id):
    """Return an order only when the caller presents its cart token."""
    cart_token = request.headers.get("X-Cart-Token")

    if not cart_token:
        return jsonify({"error": "X-Cart-Token header is required"}), 401

    order = db.session.get(Order, order_id)

    # Use the same response for unknown orders and mismatched tokens to avoid
    # exposing whether another customer's order ID exists.
    if order is None or order.cart.cart_token != cart_token:
        return jsonify({"error": "Order not found"}), 404

    return jsonify(
        {
            "id": order.id,
            "status": order.status.value,
            "total_amount": str(order.total_amount),
            "shipping_address_1": order.shipping_address_1,
            "shipping_address_2": order.shipping_address_2,
            "shipping_country": order.shipping_country,
            "shipping_city": order.shipping_city,
            "shipping_zip_code": order.shipping_zip_code,
            "shipping_state": order.shipping_state,
        }
    ), 200
