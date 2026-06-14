#!/usr/bin/env python3

# file: customers.py
# descr: external buyer who will receive the bags.
# relation wit invoice table

from __future__ import annotations # fix import from another file model
from typing import TYPE_CHECKING
import enum
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

# TODO: customer status, customer_type
class CustomerStatus(str, enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    BLOCKED = 'blocked'

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
    
    stripe_customer_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )
    
    default_payment_method_id: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    customer_status: Mapped[CustomerStatus] = mapped_column(
        db.Enum(
            CustomerSatus,
            native_enum=False,
            validate_strings=True
        ),
        nullable=False,
        default=CustomerStatus.ACTIVE,
        server_default='active'
    )
    
    customer_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    
    # one customer can have many invoices
    # use list in the many side of a relationship only
    invoices: Mapped[list["Invoice"]] = db.relationship(
        'Invoice',
        back_populates='customer',
        lazy='selectin',
    )
    
    def ensure_editable(self):
        if self.status == CustomerStatus.BLOCKED:
            raise ValueError("[ERROR] Customer blocked. Contact Admin.")