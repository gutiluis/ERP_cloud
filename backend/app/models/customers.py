#!/usr/bin/env python3

# file: customers.py
# descr: external buyer who will receive the bags.
# relation wit invoice table

from __future__ import annotations # fix import from another file model
from typing import TYPE_CHECKING
from app.extensions import (
    db,
    Mapped,
    mapped_column,
    String,
    BigInteger,
    TimeStampModel,
    Optional,
    Text
)


if TYPE_CHECKING:
    from .invoice import Invoice


class Customer(TimeStampModel):
    __tablename__ = 'customers'
    # backup in mysql too
    # biginteger does not increment automatically in sqlite. and does not autogenerate the id
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    # every customer has an invoice
    customer_id: Mapped[str] = mapped_column(
        String(50), 
        index=True, 
        unique=True, 
        nullable=False
    )

    customer_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )

    customer_email: Mapped[Optional[str]] = mapped_column(
        String(200), 
        nullable=True,
        unique=True,
        index=True
    )
    customer_phone: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True
    ) # a phone numbers are identifiers. not numbers/integers

    customer_address: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    additional_notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    # one customer can have many invoices
    # use list in the many side of a relationship only
    invoices: Mapped[list["Invoice"]] = db.relationship(
        'Invoice',
        back_populates='customer',
        lazy='selectin',
    )