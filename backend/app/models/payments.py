# file: /backend/app/models/payments.py
# descr: payments model

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.mixin import TimeStampModel

if TYPE_CHECKING:
    from .invoice import Invoice


class Payment(TimeStampModel):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # external systems stripe. requires strings
    public_payment_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    invoice_id: Mapped[int] = mapped_column(
        BigInteger,
        db.ForeignKey("invoices.id", ondelete="restrict"),
        nullable=False,
        index=True,
    )

    payment_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    payment_reference: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)

    invoice: Mapped[Invoice] = db.relationship(
        "Invoice", back_populates="payments", uselist=False
    )

    # from sqlalchemy docs typing library
    additional_info: Mapped[str | None] = mapped_column(Text, nullable=True)
