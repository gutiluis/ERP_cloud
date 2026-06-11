#!/bin/env python

'''
Tests for the Invoice, InvoiceItem, and InvoiceTax models using pytest and the test DB.

- Use the session fixture; do not use db.session directly in tests.
- Invoice requires a Customer (customer_fk_id). InvoiceItem requires a Product.
'''

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.models.invoice import Invoice, InvoiceItem, InvoiceTax, InvoiceStatus
from app.models.customers import Customer
from app.models.products import Product


def test_create_invoice(session):
    """Create an invoice with required fields and check defaults."""
    customer = Customer(
        customer_id="CUST-INV-001",
        customer_name="Invoice Test Customer",
        customer_address="123 Test St",
    )
    session.add(customer)
    session.commit()

    due = datetime.now(timezone.utc) + timedelta(days=30)
    invoice = Invoice(
        public_invoice_id="INV-001",
        customer_fk_id=customer.id,
        invoice_due_date=due,
    )
    session.add(invoice)
    session.commit()

    retrieved = session.query(Invoice).filter_by(public_invoice_id="INV-001").first()
    assert retrieved is not None
    assert retrieved.public_invoice_id == "INV-001"
    assert retrieved.customer_fk_id == customer.id
    assert retrieved.status == InvoiceStatus.pending.value
    assert retrieved.subtotal == Decimal("0.00")
    assert retrieved.tax_amount == Decimal("0.00")
    assert retrieved.shipping_amount == Decimal("0.00")
    assert retrieved.total_amount == Decimal("0.00")
    assert retrieved.outstanding_balance == Decimal("0.00")
    assert retrieved.invoice_date is not None
    assert retrieved.invoice_due_date == due
    assert retrieved.date_fully_paid is None
    assert retrieved.additional_notes is None
    assert retrieved.customer is not None
    assert retrieved.customer.customer_id == "CUST-INV-001"


def test_create_invoice_with_amounts_and_notes(session):
    """Create an invoice with amounts and optional notes."""
    customer = Customer(
        customer_id="CUST-INV-002",
        customer_name="Customer Two",
        customer_address="456 Other St",
    )
    session.add(customer)
    session.commit()

    due = datetime.now(timezone.utc) + timedelta(days=14)
    invoice = Invoice(
        public_invoice_id="INV-002",
        customer_fk_id=customer.id,
        invoice_due_date=due,
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("13.00"),
        shipping_amount=Decimal("10.00"),
        total_amount=Decimal("123.00"),
        outstanding_balance=Decimal("123.00"),
        additional_notes="Net 14.",
    )
    session.add(invoice)
    session.commit()

    retrieved = session.query(Invoice).filter_by(public_invoice_id="INV-002").first()
    assert retrieved.subtotal == Decimal("100.00")
    assert retrieved.tax_amount == Decimal("13.00")
    assert retrieved.shipping_amount == Decimal("10.00")
    assert retrieved.total_amount == Decimal("123.00")
    assert retrieved.outstanding_balance == Decimal("123.00")
    assert retrieved.additional_notes == "Net 14."


def test_invoice_status_enum(session):
    """Invoice status can be set to enum values."""
    customer = Customer(
        customer_id="CUST-INV-003",
        customer_name="Status Customer",
        customer_address="789 Status Ave",
    )
    session.add(customer)
    session.commit()

    due = datetime.now(timezone.utc) + timedelta(days=7)
    invoice = Invoice(
        public_invoice_id="INV-003",
        customer_fk_id=customer.id,
        invoice_due_date=due,
        status=InvoiceStatus.paid.value,
    )
    session.add(invoice)
    session.commit()

    retrieved = session.query(Invoice).filter_by(public_invoice_id="INV-003").first()
    assert retrieved.status == InvoiceStatus.paid.value


def test_invoice_item(session):
    """Create an invoice and an invoice item linked to a product."""
    customer = Customer(
        customer_id="CUST-INV-004",
        customer_name="Item Customer",
        customer_address="Item St",
    )
    session.add(customer)
    session.commit()

    product = Product(
        public_product_id="PID-INV-001",
        product_name="Invoice Test Product",
        sku="SKU-INV-001",
        brand="Brand",
        product_category="Category",
        product_description="For invoice item test",
    )
    session.add(product)
    session.commit()

    due = datetime.now(timezone.utc) + timedelta(days=30)
    invoice = Invoice(
        public_invoice_id="INV-004",
        customer_fk_id=customer.id,
        invoice_due_date=due,
    )
    session.add(invoice)
    session.commit()

    item = InvoiceItem(
        invoice_fk_id=invoice.id,
        product_fk_id=product.id,
        quantity=2,
        unit_price=Decimal("25.00"),
        line_total=Decimal("50.00"),
    )
    session.add(item)
    session.commit()

    retrieved = session.query(InvoiceItem).filter_by(invoice_fk_id=invoice.id).first()
    assert retrieved is not None
    assert retrieved.quantity == 2
    assert retrieved.unit_price == Decimal("25.00")
    assert retrieved.line_total == Decimal("50.00")
    assert retrieved.invoice is not None
    assert retrieved.invoice.public_invoice_id == "INV-004"

    inv = session.query(Invoice).filter_by(public_invoice_id="INV-004").first()
    assert len(inv.items) == 1
    assert inv.items[0].line_total == Decimal("50.00")


def test_invoice_tax(session):
    """Create an invoice and attach an InvoiceTax."""
    customer = Customer(
        customer_id="CUST-INV-005",
        customer_name="Tax Customer",
        customer_address="Tax Blvd",
    )
    session.add(customer)
    session.commit()

    due = datetime.now(timezone.utc) + timedelta(days=30)
    invoice = Invoice(
        public_invoice_id="INV-005",
        customer_fk_id=customer.id,
        invoice_due_date=due,
    )
    session.add(invoice)
    session.commit()

    tax = InvoiceTax(
        invoice_fk_id=invoice.id,
        tax_rate_percent=Decimal("13.00"),
        tax_amount=Decimal("13.00"),
    )
    session.add(tax)
    session.commit()

    retrieved = session.query(InvoiceTax).filter_by(invoice_fk_id=invoice.id).first()
    assert retrieved is not None
    assert retrieved.tax_rate_percent == Decimal("13.00")
    assert retrieved.tax_amount == Decimal("13.00")
    assert retrieved.invoice is not None
    assert retrieved.invoice.public_invoice_id == "INV-005"

    inv = session.query(Invoice).filter_by(public_invoice_id="INV-005").first()
    assert len(inv.taxes) == 1
    assert inv.taxes[0].tax_amount == Decimal("13.00")


def test_customer_invoices_relationship(session):
    """Customer.invoices includes all invoices for that customer."""
    customer = Customer(
        customer_id="CUST-INV-006",
        customer_name="Multi Invoice Customer",
        customer_address="Multi St",
    )
    session.add(customer)
    session.commit()

    due = datetime.now(timezone.utc) + timedelta(days=30)
    for i, pid in enumerate(["INV-006A", "INV-006B"], start=1):
        inv = Invoice(
            public_invoice_id=pid,
            customer_fk_id=customer.id,
            invoice_due_date=due,
        )
        session.add(inv)
    session.commit()

    cust = session.query(Customer).filter_by(customer_id="CUST-INV-006").first()
    assert len(cust.invoices) == 2
    ids = {inv.public_invoice_id for inv in cust.invoices}
    assert ids == {"INV-006A", "INV-006B"}


def test_invoice_timestamps(session):
    """Invoice and related models inherit TimeStampModel (created/updated)."""
    customer = Customer(
        customer_id="CUST-INV-007",
        customer_name="Timestamp Customer",
        customer_address="Time St",
    )
    session.add(customer)
    session.commit()

    due = datetime.now(timezone.utc) + timedelta(days=30)
    invoice = Invoice(
        public_invoice_id="INV-007",
        customer_fk_id=customer.id,
        invoice_due_date=due,
    )
    session.add(invoice)
    session.commit()

    retrieved = session.query(Invoice).filter_by(public_invoice_id="INV-007").first()
    assert retrieved.created is not None
    assert retrieved.updated is not None

    tax = InvoiceTax(
        invoice_fk_id=retrieved.id,
        tax_rate_percent=Decimal("8.50"),
        tax_amount=Decimal("8.50"),
    )
    session.add(tax)
    session.commit()

    retrieved_tax = session.query(InvoiceTax).filter_by(invoice_fk_id=retrieved.id).first()
    assert retrieved_tax.created is not None
    assert retrieved_tax.updated is not None
