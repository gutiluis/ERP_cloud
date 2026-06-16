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
    Text,
    text,
    UniqueConstraint,
    Index
)


if TYPE_CHECKING:
    from .invoice import Invoice
    from .orders import Order


class CustomerStatus(str, enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    BLOCKED = 'blocked'
    

class CustomerType(str, enum.Enum):
    BUSINESS = 'business'
    INDIVIDUAL = 'individual'

# does the table require constraints, indexes or other database-level configuration/rules
class Customer(TimeStampModel):
    __tablename__ = 'customers'
    __table_args__ = (
        Index("ix_customer_status", "customer_status"), 
        # every single row in that column must have a completely different value
        UniqueConstraint("customer_id"),
    )
    {
        "mysql_engine": "InnoDB"
    }

    # backup in mysql too
    # biginteger does not increment automatically in sqlite. and does not autogenerate the id
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    # exception integrity error
    # every customer has an invoice
    customer_id: Mapped[str] = mapped_column(
        String(50), 
        index=True, 
        unique=True, 
        nullable=False
    )

    # exception integrity error
    customer_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        unique=True
    )

    # exception integrityerror
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
        nullable=True
    )
    
    additional_notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    
    customer_status: Mapped[CustomerStatus] = mapped_column(
        db.Enum(
            CustomerStatus,
            native_enum=False,
            validate_strings=True
        ),
        nullable=False,
        default=CustomerStatus.ACTIVE,
        server_default=text("'active'")
    )

    customer_type: Mapped[CustomerType] = mapped_column(
        db.Enum(
            CustomerType,
            # native_enum helps migrations complexity
            native_enum=False,
            validate_strings=True
        ),
        nullable=False,
        # default is sqlalchemy/python side
        default=CustomerType.BUSINESS,
        # server_default is database side
        server_default=text("'business'")
    )
    

    # one customer can have many invoices
    # use list in the many side of a relationship only
    invoices: Mapped[list["Invoice"]] = db.relationship(
        'Invoice',
        back_populates='customer',
        lazy='selectin',
    )
    
    # class attribute orders.
    # lazy='selectin' is a relationship loading style
    # back_populates is not a parameter of the class attribute. is a parameter of relationship()
    orders: Mapped[list["Order"]] = db.relationship(
        'Order',
        back_populates='customer',
        lazy='selectin',
    )
    
    def ensure_editable(self):
        if self.status == CustomerStatus.BLOCKED:
            raise ValueError("[ERROR] Customer blocked. Contact Admin.")
