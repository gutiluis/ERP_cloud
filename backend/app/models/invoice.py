#!/usr/bin/env python3


# filename: invoice.py
# descr: invoice calculates subtotal, discount, tax total. Invoice Item subtotal



from __future__ import annotations # fix declarative mapping relationship with annotation from another file
from typing import TYPE_CHECKING # fix declarative mapping relationship with annotation from another file

from datetime import datetime, timezone
from decimal import Decimal
import enum

from app.extensions import (
    db,
    Mapped,
    mapped_column,
    String,
    TimeStampModel,
    BigInteger,
    Numeric,
    DateTime,
    Optional,
    Text,
    text,
    Enum,
    func,
    Index,
    CheckConstraint
)

if TYPE_CHECKING: # fix import relationship from another file
    from .customers import Customer
    from .payments import Payment
    from .products import Product




class InvoiceStatus(str, enum.Enum):
    DRAFT = 'draft'
    ISSUED = 'issued'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    VOID = 'void'


class Invoice(TimeStampModel):
    __tablename__ = "invoices"
    
    __table_args__ = (
        Index("ix_invoice_customer", "customer_id"),
        Index("ix_invoice_status", "status"),
        Index("ix_invoice_customer_status", "customer_id", "status"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    public_invoice_id: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True
    )

    customer_id: Mapped[int] = mapped_column(
        BigInteger, 
        db.ForeignKey('customers.id',
                      ondelete='RESTRICT'
        ),
        nullable=False, 
        index=True
    )
    
    # a relationship with annotations does not have nullable=False
    customer: Mapped["Customer"] = db.relationship(
        "Customer", 
        back_populates="invoices",
        lazy='selectin'
    )

    status: Mapped[InvoiceStatus] = mapped_column(
        db.Enum(
            InvoiceStatus,
            native_enum=False,
            validate_strings=True
        ),
        nullable=False,
        default=InvoiceStatus.DRAFT,
        server_default="draft"
    )
    
    invoice_date: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )
    
    invoice_due_date: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False
    )

    payments: Mapped[list["Payment"]] = db.relationship(
        "Payment", 
        # the name of the table is invoice or invoices?
        back_populates="invoice",
        lazy='selectin',
        cascade='save-update, merge'
    )
    
    # see invoicetaxes relationship annotated mapping
    taxes: Mapped[list["InvoiceTax"]] = db.relationship(
        "InvoiceTax", 
        # the name of the table is invoices or invoice?
        back_populates="invoice", 
        cascade="all, delete-orphan", 
        lazy="selectin"
    )

    additional_notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        server_default=text("0.00")
    )
    
    items: Mapped[list["InvoiceItem"]] = db.relationship(
        "InvoiceItem",
        # the name of the table is invoice or invoices?
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        server_default=text("'USD'"),
        index=True
    )
    
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        server_default=text("0.00")
    )
    
    def ensure_editable(self):
        if self.status in (InvoiceStatus.PAID, InvoiceStatus.VOID):
            raise ValueError("Invoice is locked")
    
    
    def recalc_invoice(self):
        self.ensure_editable()
        # access the property in the invoiceitem class. no need for self class attribute
        # subtotal is local variable no need for class attribute named subtotal
        subtotal = sum(i.line_total for i in self.items)
        # tax_total is a local variable. no need for tax_total class attribute
        tax_total = sum(t.tax_amount for t in self.taxes)
        self.total_amount = subtotal + tax_total

    def sync_totals(self, item):
        self.ensure_editable()
        self.items.append(item)
        db.session.flush()

class InvoiceItem(TimeStampModel):
    __tablename__ = "invoice_items"

    __table_args__ = (
        Index("ix_quantity", "quantity"),
        Index("ix_unit_price", "unit_price"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    invoice_id: Mapped[int] = mapped_column(
        BigInteger, 
        db.ForeignKey("invoices.id", ondelete='restrict'),
        nullable=False,
        index=True
    )
    
    product_id: Mapped[int] = mapped_column(
        BigInteger, 
        db.ForeignKey("products.id"), 
        nullable=False, 
        index=True
    )

    quantity: Mapped[int] = mapped_column(
        BigInteger, 
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        # server_default is more secure
        server_default=text("0.00")
    )
    
    invoice: Mapped["Invoice"] = db.relationship(
        "Invoice", 
        back_populates='items'
    )

    product_name: Mapped["Product"]  = db.relationship("Product")

    # can be used within other classes
    @property
    def line_total(self) -> Decimal:
        return Decimal(self.quantity) * Decimal(self.unit_price)


class InvoiceTax(TimeStampModel):
    __tablename__ = 'invoice_taxes'
    # declarative style system
    # querying
    # __table_args__ is a class attribute
    # index=True is not the same Index
    # use __table_args__ to specify table arguments other than args(name, metadata, and mapped_column args)
    __table_args__ = (
        Index("ix_invoice_tax_invoice_id", "invoice_id"),
        Index("ix_invoice_tax_type", "tax_type"),
        CheckConstraint("tax_rate_percent >= 0 AND tax_rate_percent <= 100"),
        CheckConstraint("tax_base >= 0"),
        CheckConstraint("tax_amount >= 0"),
        # class attribute specified as a dictionary of __table_args__ in docs
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
    
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )
    
    invoice_id: Mapped[int] = mapped_column(
        BigInteger, 
        db.ForeignKey("invoices.id", ondelete='restrict'),
        nullable=False
    )
    
    tax_type: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True
    )
    
    tax_rate_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), 
        nullable=False
    )
    
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), 
        nullable=False
    )
    
    tax_base: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    invoice: Mapped["Invoice"] = db.relationship(
        "Invoice", 
        back_populates="taxes"
    )
