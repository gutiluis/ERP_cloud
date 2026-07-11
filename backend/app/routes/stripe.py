#!/usr/bin/env python3


"""
# file: /app/routes/stripe.py

# descr: make a new invoice from the stripe payment and do not make the routes/invoice.py route
# listen for events from stripe on webhook endpoint so integration can automatically trigger reactions
# event object with json payload
# webhook events help respond to asynchronous events, such as when a customer's bank confirms a payment, a customer disputes a charge, or a recurring payment succeeds
"""


import stripe
from stripe.error import SignatureVerificationError
from flask import Blueprint, request, current_app
from app import db
from app.models.invoice import Invoice
from app import config
from decimal import Decimal

stripe_bp = Blueprint(
    "stripe",
    __name__,
    url_prefix="/api/admin/stripe"
)


@stripe_bp.route("/webhook", methods=["POST"])
def webhook():
    # all event share same structure except data property
    # event body
    payload = request.data
    # signature parameter for constructEvent()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            # import config.py
            # endpoint secret associated parameter for construct_event
            current_app.config["STRIPE_WEBHOOK_SECRET"]
        )
    except ValueError:
        # 400 bad request
        abort(400)
        # verify webhook authenticity
    except SignatureVerificationError:
        abort(400)

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        order_id = session.get("metadata", {}).get("order_id")
        if not order_id:
            return {"error": "missing_order_id"}, 400

        order = db.session.query(Order).filter_by(id=order_id).first()

        if not order:
            return {"error": "order_not_found"}, 404

        existing_invoice = db.session.query(Invoice).filter_by(
            stripe_session_id=session["id"]
        ).first()

        if existing_invoice:
            return {"ok": True}

        order.status = "paid"

        invoice=Invoice(
            stripe_session_id=session["id"],
            stripe_payment_intent_id=session.get("payment_intent"),
            status="paid",
            currency=session.get("currency"),
            stripe_checkout=session["created"],
            customer_id=order.customer_id,
        )
        for copy_item_from_order in order.items:
            invoice_item = InvoiceItem(
                product_id=copy_item_from_order.product_id,
                quantity=copy_item_from_order.quantity,
                unit_price=copy_item_from_order.unit_price,
            )
            invoice.items.append(invoice_item)
        db.session.add(invoice)
        db.session.commit()
        return {"success": True}
    return {"ignored": True}, 200
