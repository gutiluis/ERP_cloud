#!/usr/bin/env python3

# file: /app/routes/invoices.py
# descr: invoices admin private routes by stripe payments


from app import db
from app.models import Invoice, InvoiceItem, InvoiceTax
from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import login_required
from datetime import datetime

invoice_bp = Blueprint(
    "invoices",
    __name__,
    url_prefix="/api/admin/invoices"
)


@invoice_bp.route("/")
@login_required
def index_all_invoices():
    """
    Admin Index all invoices
    """
    invoices = db.session.execute(
            db.select(Invoice).order_by(Invoice.invoice_id)).scalars().all()
    return render_template("invoices/index.html",
                           invoices=invoices
    )


@invoice_bp.route("/<string:invoice_id>", methods=["GET"])
@login_required
def invoice_detail(invoice_id):
    """
    Admin get invoice details
    """
    invoice = db.session.execute(db.select(Invoice).filter_by(invoice_id=invoice_id)).scalar_one().get_or_404()
    return render_template("invoices/invoicedetail.html")


@invoice_bp.route("/void/<string:invoice_id>", methods=["POST"])
@login_required
def void_invoice(invoice_id):
    invoice = db.session.execute(db.select(Invoice).order_by(Invoice.invoice_id)).scalars.get_or_404()
    if not invoice:
        abort(403)
    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for("invoices.index_all_invoices"))
