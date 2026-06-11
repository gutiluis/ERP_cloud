#!/user/bin/env python3

# filename: products.py
# descr: static catalog. relationship with orders.py

from __future__ import annotations
from typing import TYPE_CHECKING
from decimal import Decimal

from app.extensions import (
    db,
    Mapped,
    mapped_column,
    BigInteger,
    String,
    Boolean,
    Numeric,
    TimeStampModel,
    Optional,
    Integer,
    Text,
    text
)

if TYPE_CHECKING:
    from .orders import Order

class Product(TimeStampModel):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )
    
    public_product_id: Mapped[str] = mapped_column(
        String(50), 
        index=True, 
        unique=True, 
        nullable=False
    )

    product_name: Mapped[str] = mapped_column(
        String(200), 
        nullable=False
    )
    
    brand: Mapped[str] = mapped_column(
        String(200), 
        nullable=False, 
        index=True
    )
    
    product_category: Mapped[str] = mapped_column(
        String(200), 
        nullable=False, 
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        server_default=text("1")
    )
    
    product_description: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    
    orders: Mapped[list["Order"]] = db.relationship(
        "Order",
        back_populates="product"
    )
    
    # text cannot be indexed
    # If a column is unique=True or index=True, it must be String(n) in MySQL.
    # 3072 bytes = 768 characters in utf8mb4
    url: Mapped[str] = mapped_column(
        String(760), 
        unique=True, 
        nullable=False
    )
    url_tag: Mapped[str] = mapped_column(
        String(100), 
        nullable=True
    )
    
    additional_notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )

    variants = db.relationship(
        'ProductVariant',
        back_populates='product',
        cascade='all, delete-orphan', # parent-child ownership
        lazy='selectin', # avoids n+1 queries when loading products with variants
    )


class ProductVariant(TimeStampModel):
    __tablename__ = 'product_variants'
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, autoincrement=True
    )

    product_id: Mapped[int] = mapped_column(
        db.ForeignKey('products.id'), 
        nullable=False, 
        index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1") # db
    )
    color: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        # text('0') is sql expression not Text column types
        nullable=False, server_default=text("0")
    )

    sku: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    stripe_price_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    stripe_product_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    
    is_external: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0")
    )

    external_source: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    
    external_product_id: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    
    product = db.relationship(
        'Product',
        back_populates='variants',
    )
    
    @property
    def is_in_stock(self) -> bool:
        return self.is_active and self.stock_quantity > 0