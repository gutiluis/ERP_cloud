#!/usr/bin/env python3


"""
# file: /app/routes/stripe.py

# descr: make a new invoice from the stripe payment and do not make the routes/invoice.py route
# listen for events from stripe on webhook endpoint so integration can automatically trigger reactions
# event object with json payload
# webhook events help respond to asynchronous events, such as when a customer's bank confirms a payment, a customer disputes a charge, or a recurring payment succeeds
"""


import stripe

from flask import Blueprint, request, current_app
from app import db
from app.models.invoices import Invoice


stripe_bp = Blueprint(
    "stripe",
    __name__,
    url_prefix="/api/admin/stripe"
)

@stripe_bp.route("/webhook", methods=["POST"])
def webhook():
    payload
