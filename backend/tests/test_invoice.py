"""
file: tests/test_invoice.py
descr:
Tests for the Invoice, InvoiceItem, and InvoiceTax models using pytest and the test DB.

- Use the session fixture; do not use db.session directly in tests.
- Invoice requires a Customer (customer_id). InvoiceItem requires a Product.
"""

from decimal import Decimal

from app.models.admin_user import AdminUser
from app.models.cart import Cart
from app.models.customers import Customer
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, InvoiceTax
from app.models.orders import Order, OrderStatus
from app.models.products import Product


def create_admin(session):
    admin = AdminUser(
        admin_id="ADM-TEST-001",
        username="invoice_test_admin",
        email="invoice-test@example.com",
        password_hash="test-password-hash",
    )
    session.add(admin)
    session.flush()
    return admin


def create_customer(session):
    customer = Customer(
        customer_id="CUS-TEST-001",
        customer_name="Invoice Test Customer",
        customer_email="invoice-customer@example.com",
    )
    session.add(customer)
    session.flush()
    return customer


def create_product(session, customer):
    product = Product(
        product_id="PROD-TEST-001",
        product_name="Invoice Test Product",
        customer_id=customer.customer_id,
        brand="Test Brand",
        category="Test Category",
        is_active=True,
        description="Product used for invoice tests.",
    )
    session.add(product)
    session.flush()
    return product


def create_cart(session):
    cart = Cart(
        cart_token="invoice-test-cart-001",
        total_amount=Decimal("100.00"),
    )
    session.add(cart)
    session.flush()
    return cart


def create_order(session, admin, customer, cart):
    order = Order(
        stripe_session_id="cs_invoice_test_001",
        operator_admin_id=admin.id,
        customer_id=customer.id,
        cart_id=cart.id,
        status=OrderStatus.PENDING,
        total_amount=Decimal("100.00"),
        shipping_address_1="123 Test Street",
        shipping_country="Mexico",
        shipping_city="Guadalajara",
        shipping_zip_code="44100",
        shipping_state="Jalisco",
    )
    session.add(order)
    session.flush()
    return order


def create_invoice(session, customer, order):
    invoice = Invoice(
        invoice_id="INV-TEST-001",
        customer_id=customer.id,
        order_id=order.id,
        status=InvoiceStatus.DRAFT,
        total_amount=Decimal("100.00"),
    )
    session.add(invoice)
    session.flush()
    return invoice


def test_create_invoice(session):
    admin = create_admin(session)
    customer = create_customer(session)
    cart = create_cart(session)
    order = create_order(session, admin, customer, cart)

    invoice = create_invoice(session, customer, order)

    assert invoice.id is not None
    assert invoice.invoice_id == "INV-TEST-001"
    assert invoice.customer_id == customer.id
    assert invoice.order_id == order.id
    assert invoice.status == InvoiceStatus.DRAFT


def test_create_invoice_with_amounts_and_notes(session):
    admin = create_admin(session)
    customer = create_customer(session)
    cart = create_cart(session)
    order = create_order(session, admin, customer, cart)

    invoice = Invoice(
        invoice_id="INV-TEST-002",
        customer_id=customer.id,
        order_id=order.id,
        total_amount=Decimal("108.00"),
        discount_amount=Decimal("5.00"),
        discount_percentage=Decimal("5.00"),
        additional_notes="Test invoice notes.",
        currency="MXN",
    )

    session.add(invoice)
    session.flush()

    assert invoice.total_amount == Decimal("108.00")
    assert invoice.discount_amount == Decimal("5.00")
    assert invoice.discount_percentage == Decimal("5.00")
    assert invoice.additional_notes == "Test invoice notes."
    assert invoice.currency == "MXN"


def test_invoice_status_enum(session):
    admin = create_admin(session)
    customer = create_customer(session)
    cart = create_cart(session)
    order = create_order(session, admin, customer, cart)

    invoice = create_invoice(session, customer, order)

    assert invoice.status == InvoiceStatus.DRAFT

    invoice.status = InvoiceStatus.ISSUED
    session.flush()
    assert invoice.status == InvoiceStatus.ISSUED

    invoice.status = InvoiceStatus.PAID
    session.flush()
    assert invoice.status == InvoiceStatus.PAID

    invoice.status = InvoiceStatus.CANCELLED
    session.flush()
    assert invoice.status == InvoiceStatus.CANCELLED

    invoice.status = InvoiceStatus.VOID
    session.flush()
    assert invoice.status == InvoiceStatus.VOID


def test_invoice_item(session):
    admin = create_admin(session)
    customer = create_customer(session)
    product = create_product(session, customer)
    cart = create_cart(session)
    order = create_order(session, admin, customer, cart)
    invoice = create_invoice(session, customer, order)

    item = InvoiceItem(
        invoice_id=invoice.id,
        product_id=product.id,
        quantity=2,
        unit_price=Decimal("25.00"),
    )

    session.add(item)
    session.flush()

    assert item.id is not None
    assert item.invoice_id == invoice.id
    assert item.product_id == product.id
    assert item.quantity == 2
    assert item.unit_price == Decimal("25.00")
    assert item.line_total == Decimal("50.00")
    assert item in invoice.items


def test_invoice_tax(session):
    admin = create_admin(session)
    customer = create_customer(session)
    cart = create_cart(session)
    order = create_order(session, admin, customer, cart)
    invoice = create_invoice(session, customer, order)

    tax = InvoiceTax(
        invoice_id=invoice.id,
        tax_type="VAT",
        tax_rate_percent=Decimal("16.0000"),
        tax_amount=Decimal("16.00"),
        tax_base=Decimal("100.00"),
    )

    session.add(tax)
    session.flush()

    assert tax.id is not None
    assert tax.invoice_id == invoice.id
    assert tax.tax_type == "VAT"
    assert tax.tax_rate_percent == Decimal("16.0000")
    assert tax.tax_amount == Decimal("16.00")
    assert tax.tax_base == Decimal("100.00")
    assert tax in invoice.taxes


def test_customer_invoices_relationship(session):
    admin = create_admin(session)
    customer = create_customer(session)
    cart = create_cart(session)
    order = create_order(session, admin, customer, cart)

    invoice = create_invoice(session, customer, order)

    session.refresh(customer)

    assert invoice in customer.invoices
    assert invoice.customer == customer


def test_invoice_timestamps(session):
    admin = create_admin(session)
    customer = create_customer(session)
    cart = create_cart(session)
    order = create_order(session, admin, customer, cart)

    invoice = create_invoice(session, customer, order)

    assert invoice.created is not None
    assert invoice.updated is not None
