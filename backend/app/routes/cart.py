# file: /routes/cart.py
# descr: cart does not require login. the stripe and checkout webhook need the cart as buyers and sellers do not have login accounts. only a cart_token

from uuid import uuid4
from decimal import Decimal
from app import db
from app.models.cart import Cart, CartItem
from app.models.products import ProductVariant
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


@cart_bp.route("", methods=["POST"])
def create_cart():
    """
    Backend stores actual cart and cart items in the db.
    Buyer creates cart without flask-login account registration
    Frontend stores only the cart identifier to relief stress from backend server
    Frontend calls sends request
    """
    data = request.get_json(silent=True) or {}
    product_variant_id = data.get("product_variant_id")
    quantity = data.get("quantity")

    if not isinstance(product_variant_id, int):
        return jsonify({"error": "product_variant_id is required"}), 400
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "quantity must be greater than zero"}), 400

    variant = (
        db.session.execute(
            db.select(ProductVariant).where(
                ProductVariant.id == product_variant_id,
                ProductVariant.is_active.is_(True),
            )
        )
        .scalars()
        .first()
    )

    if variant is None:
        return jsonify({"error": "Product variant not found"}), 404
    if quantity > variant.stock_quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    customer = variant.product.customer

    if customer is None:
        return jsonify({"error": "Product customer not found"}), 404

    cart = Cart(
        cart_token=str(uuid4()),
        customer_id=customer.id,
        total_amount=Decimal("0.00"),
    )

    item = CartItem(
        cart=cart,
        product_id=variant.product_id,
        product_variant_id=variant.id,
        quantity=quantity,
        unit_price=variant.price,
    )

    try:
        db.session.add(item)

        cart.total_amount = variant.price * quantity

        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        current_app.logger.exception("an error occurred")
        # for json use jsonify instead of abort
        return jsonify({"error": "Database constraint error"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error. Cart wasn't created")
        return jsonify({"error": "Database error"}), 500
    # make_response can help to set additional heares, change status code of response and attach cookies wrapping json
    # jsonify from flask allows data to be converted and returned as a response object to the client with the Content-Type header automatically set to application/json
    return jsonify(
        {"message": "Cart created successfully.", "cart_token": cart.cart_token}
    ), 201


@cart_bp.route("/<cart_token>", methods=["GET"])
def get_cart(cart_token):
    """
    Buyer's cart without customer_id
    """
    cart = Cart.query.filter_by(cart_token=cart_token).first_or_404()

    return jsonify(
        {
            "cart_token": cart.cart_token,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_variant_id": item.product_variant_id,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                }
                for item in cart.items
            ],
            "total_amount": str(cart.total_amount),
        }
    ), 200


@cart_bp.route("/<cart_token>/items", methods=["POST"])
def add_item(cart_token):
    """Find the cart by cart_token, validate product_variant_id, validate positive quantity, find the active variant, check stock, check whether that variant already exists in the cart, increate variants quantity, otherwise create cartitem, recalculate cart.total_amount, commit"""

    cart = Cart.query.filter_by(cart_token=cart_token).first_or_404()
    # multipurpose internet mail extensions type
    # silence=True # silence mimetype and parsing errors, and return None instead
    # application/json is MIME type media type specified by the header
    # Content-Type: application/json
    data = request.get_json(silent=True) or {}

    product_variant_id = data.get("product_variant_id")
    quantity = data.get("quantity")

    if not isinstance(product_variant_id, int):
        return jsonify({"error": "product_variant_id is required"}), 400

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "quantity must be greater than zero"}), 400

    variant = (
        db.session.execute(
            db.select(ProductVariant).where(
                ProductVariant.id == product_variant_id,
                ProductVariant.is_active.is_(True),
            )
        )
        .scalars()
        .first()
    )

    if variant is None:
        return jsonify({"error": "Product variant not found"}), 404

    if variant.product.customer.id != cart.customer_id:
        return jsonify({"error": "Product does not belong to this seller"}), 400

    item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_variant_id=variant.id,
    ).first()

    new_quantity = quantity if item is None else item.quantity + quantity

    if new_quantity > variant.stock_quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    if item is None:
        item = CartItem(
            cart_id=cart.id,
            product_id=variant.product_id,
            product_variant_id=variant.id,
            quantity=quantity,
            unit_price=variant.price,
        )
        db.session.add(item)
    else:
        item.quantity = new_quantity
        item.unit_price = variant.price

    cart.total_amount = sum(
        (cart_item.unit_price * cart_item.quantity for cart_item in cart.items),
        Decimal("0.00"),
    )

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error. Item wasn't added")
        return jsonify({"error": "Database error"}), 500

    return jsonify(
        {
            "message": "Item added successfully.",
            "cart_token": cart.cart_token,
            "item": {
                "id": item.id,
                "product_id": item.product_id,
                "product_variant_id": item.product_variant_id,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
            },
            "total_amount": str(cart.total_amount),
        }
    ), 201


# idempotence: applied multiple times without changing the result beyond the initial application
# patch is neithg safe nor idempotent
@cart_bp.route("/<string:cart_token>/items/<int:item_id>", methods=["PATCH"])
def update_item(cart_token, item_id):
    cart = Cart.query.filter_by(cart_token=cart_token).first_or_404()

    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    # 400 Bad request
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "quantity must be greater than zero"}), 400

    item = CartItem.query.filter_by(
        id=item_id,
        cart_id=cart.id,
    ).first()

    if item is None:
        return jsonify({"error": "Cart item not found"}), 404
    # avoid remaining cart items
    if not item.product_variant.is_active:
        return jsonify({"error": "Product variant not found"}), 404
    # stock validation
    if quantity > item.product_variant.stock_quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    item.quantity = quantity
    # authoritative price
    item.unit_price = item.product_variant.price
    # total recalculation
    cart.total_amount = sum(
        (cart_item.unit_price * cart_item.quantity for cart_item in cart.items),
        Decimal("0.00"),
    )
    # transaction handling
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.logger.exception("Database constraint error")
        return jsonify({"error": "Database constraint error"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error. Item wasn't updated")
        return jsonify({"error": "Database error"}), 500

    return jsonify(
        {
            "message": "Item updated successfully.",
            "cart_token": cart.cart_token,
            "item": {
                "id": item.id,
                "product_id": item.product_id,
                "product_variant_id": item.product_variant_id,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
            },
            "total_amount": str(cart.total_amount),
        }
    ), 200


@cart_bp.route("/<string:cart_token>/items/<int:item_id>", methods=["DELETE"])
def delete_item(cart_token, item_id):
    """
    item - Buyer can't delete an item from another cart just by knowing its item_id
    """
    cart = Cart.query.filter_by(cart_token=cart_token).first_or_404()

    item = CartItem.query.filter_by(
        id=item_id,
        cart_id=cart.id,
    ).first()

    if item is None:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(item)
    try:
        # flush makes the state transition explicit before calculatint the total
        db.session.flush()

        # delete the item calculate the total from the remaining items
        cart.total_amount = sum(
            (cart_item.unit_price * cart_item.quantity for cart_item in cart.items),
            Decimal("0.00"),
        )

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.logger.exception("Database constraint error")
        return jsonify({"error": "Database constraint error"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error. Item wasn't deleted")
        return jsonify({"error": "Database error"}), 500

    return jsonify(
        {
            "message": "Item deleted successfully.",
            "cart_token": cart.cart_token,
            "total_amount": str(cart.total_amount),
        }
    ), 200
