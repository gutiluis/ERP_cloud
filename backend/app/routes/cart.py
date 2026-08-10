#!/usr/bin/env python3

# file: /routes/cart.py
# descr: cart does not require login. the stripe and checkout webhook need the cart as buyers and sellers do not have login accounts. only a cart_token

from flask import Blueprint, redirect, url_for, abort, flash, jsonify
from app import db
from sqlalachemy.exc import SqlAlchemyError, IntegrityError
from uuid import uuid4
from app.models.cart import Cart



cart_bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/api/cart"
)

@cart_bp.route("", methods=["POST"])
def create_cart():
    """
    Backend stores actual cart and cart items in the db.
    Buyer creates cart without flask-login account registration
    Frontend stores only the cart identifier to relief stress from backend server
    Frontend calls sends request
    """
    # import Cart model
    cart = Cart(
        cart_token=str(uuid4())
    )
    try:
        db.session.add(cart)
        db.session.commit()
        
    except IntegrityError as err:
        db.session.rollback()
        current_app.logger.exception(err)
        # for json use jsonify instead of abort
        return jsonify({
            "error", "Dublicate cart token"
        }), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            "error", "Database Error"
        }), 500
    except Exception:
        db.session.rollback()
        return jsonify({
            "error", "Unexpected Error"
        }), 500
    # make_response can help to set additional heares, change status code of response and attach cookies wrapping json
    # jsonify from flask allows data to be converted and returned as a response object to the client with the Content-Type header automatically set to application/json
    return jsonify({
        "message": "Cart created successfully.",
        "cart_token": cart.cart_token
    }), 201
    

@cart_bp.route("/<int:cart_id>", methods=["GET"])
def get_cart(cart_id):
    ...

@cart_bp.route("/<int:cart_id>/items", methods=["POST"])
def add_item(cart_id):
    ...

@cart_bp.route("/<int:cart_id>/items/<int:item_id>", methods=["PATCH"])
def update_item(cart_id, item_id):
    ...

@cart_bp.route("/<int:cart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item(cart_id, item_id):
    ...


