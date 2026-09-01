# file: /app/models/customers.py
# descr: external buyer who will receive the products.
# relation with invoice table

from __future__ import annotations

from typing import TYPE_CHECKING  # fix import from another file model

if TYPE_CHECKING:
    from app.models.invoice import Invoice
    from app.models.orders import Order
    from app.models.products import Product
    from app.models.cart import Cart

import enum

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import (
    db,
)
from app.models.mixin import TimeStampModel


class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class CustomerType(str, enum.Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"


# does the table require constraints, indexes or other database-level configuration/rules
class Customer(TimeStampModel):
    __tablename__ = "customers"
    __table_args__ = (
        # every single row in that column must have a completely different value
        UniqueConstraint("customer_id"),
        {"mysql_engine": "InnoDB"},
    )
    # backup in mysql too
    # biginteger does not increment automatically in sqlite. and does not autogenerate the id
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # exception integrity error
    # every customer has an invoice
    customer_id: Mapped[str] = mapped_column(
        String(50), index=True, unique=True, nullable=False
    )
    # exception integrity error
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    # exception integrityerror
    customer_email: Mapped[str | None] = mapped_column(
        String(200), nullable=True, unique=True, index=True
    )
    customer_phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # phone numbers are identifiers. not numbers/integers
    customer_address: Mapped[str] = mapped_column(Text, nullable=True)

    carts: Mapped[list[Cart]] = db.relationship(
        "Cart",
        back_populates="customer",
    )

    products: Mapped[list[Product]] = db.relationship(
        "Product", back_populates="customer"
    )

    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # class enum.Enum Enum is the base class for all enum enumerations
    # Color.Blue.name
    # cusotomer.customerstatus.name
    customer_status: Mapped[CustomerStatus] = mapped_column(
        db.Enum(CustomerStatus, native_enum=False, validate_strings=True),
        nullable=False,
        default=CustomerStatus.ACTIVE,
        server_default=text("'active'"),
    )

    customer_type: Mapped[CustomerType] = mapped_column(
        db.Enum(
            CustomerType,
            # native_enum helps migrations complexity
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        # default is sqlalchemy/python side
        default=CustomerType.BUSINESS,
        # server_default is database side
        server_default=text("'business'"),
    )

    # one customer can have many invoices
    # use list in the many side of a relationship only
    invoices: Mapped[list[Invoice]] = db.relationship(
        "Invoice",
        back_populates="customer",
        lazy="selectin",
    )

    # lazy='selectin' is a relationship loading style
    # back_populates is not a parameter of the class attribute. is a parameter of relationship()
    orders: Mapped[list[Order]] = db.relationship(
        "Order",
        back_populates="customer",
        lazy="selectin",
    )

    def ensure_editable(self):
        if self.status == CustomerStatus.BLOCKED:
            raise ValueError("[ERROR] Customer blocked. Contact Admin.")
