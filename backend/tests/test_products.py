#!/bin/env python

'''
Tests for the Product and ProductVariant models using pytest and the test DB.

- Use the session fixture; do not use db.session directly in tests.
'''

import pytest
from decimal import Decimal
from app.models.products import Product, ProductVariant
from app.extensions import db


def test_create_product(session):
    """Create a product with required fields and check defaults."""
    product = Product(
        public_product_id="PID-001",
        product_name="Test Product",
        sku="SKU-001",
        brand="TestBrand",
        product_category="Electronics",
        product_description="A test product description.",
    )
    session.add(product)
    session.commit()

    retrieved = session.query(Product).filter_by(public_product_id="PID-001").first()
    assert retrieved is not None
    assert retrieved.product_name == "Test Product"
    assert retrieved.sku == "SKU-001"
    assert retrieved.brand == "TestBrand"
    assert retrieved.product_category == "Electronics"
    assert retrieved.product_description == "A test product description."
    assert retrieved.is_active is True
    assert retrieved.url is None
    assert retrieved.additional_notes is None


def test_create_product_with_optionals(session):
    """Create a product with optional fields set."""
    product = Product(
        public_product_id="PID-002",
        product_name="Product With URL",
        sku="SKU-002",
        brand="Brand",
        product_category="Category",
        product_description="Description",
        url="https://example.com/product-with-url",
        url_tag="tag",
        additional_notes="Some notes",
    )
    session.add(product)
    session.commit()

    retrieved = session.query(Product).filter_by(public_product_id="PID-002").first()
    assert retrieved.url == "https://example.com/product-with-url"
    assert retrieved.url_tag == "tag"
    assert retrieved.additional_notes == "Some notes"


def test_create_product_variant(session):
    """Create a product and a variant linked to it."""
    product = Product(
        public_product_id="PID-003",
        product_name="Parent Product",
        sku="SKU-003",
        brand="Brand",
        product_category="Category",
        product_description="Description",
    )
    session.add(product)
    session.commit()

    variant = ProductVariant(
        product_fk_id=product.id,
        price=Decimal("19.99"),
        inventory_stock=100,
        color="Blue",
        size="M",
    )
    session.add(variant)
    session.commit()

    retrieved = session.query(ProductVariant).filter_by(product_fk_id=product.id).first()
    assert retrieved is not None
    assert retrieved.price == Decimal("19.99")
    assert retrieved.inventory_stock == 100
    assert retrieved.color == "Blue"
    assert retrieved.size == "M"
    assert retrieved.is_active is True
    assert retrieved.has_stock is False
    assert retrieved.parent is not None
    assert retrieved.parent.public_product_id == "PID-003"


def test_product_children_variants_relationship(session):
    """Product children_variants relationship and defaults on variant."""
    product = Product(
        public_product_id="PID-004",
        product_name="Product With Variants",
        sku="SKU-004",
        brand="Brand",
        product_category="Category",
        product_description="Description",
    )
    session.add(product)
    session.flush()

    v1 = ProductVariant(
        product_fk_id=product.id,
        price=Decimal("10.00"),
        inventory_stock=5,
    )
    v2 = ProductVariant(
        product_fk_id=product.id,
        price=Decimal("20.00"),
        inventory_stock=10,
        has_stock=True,
    )
    session.add_all([v1, v2])
    session.commit()

    product = session.query(Product).filter_by(public_product_id="PID-004").first()
    assert len(product.children_variants) == 2
    prices = {v.price for v in product.children_variants}
    assert prices == {Decimal("10.00"), Decimal("20.00")}
    assert v2.has_stock is True


def test_product_and_variant_timestamps(session):
    """Product and ProductVariant inherit TimeStampModel (created/updated)."""
    product = Product(
        public_product_id="PID-005",
        product_name="Timestamp Product",
        sku="SKU-005",
        brand="Brand",
        product_category="Category",
        product_description="Description",
    )
    session.add(product)
    session.commit()

    retrieved_product = session.query(Product).filter_by(public_product_id="PID-005").first()
    assert retrieved_product.created is not None
    assert retrieved_product.updated is not None

    variant = ProductVariant(
        product_fk_id=retrieved_product.id,
        price=Decimal("1.00"),
        inventory_stock=0,
    )
    session.add(variant)
    session.commit()

    retrieved_variant = session.query(ProductVariant).filter_by(
        product_fk_id=retrieved_product.id
    ).first()
    assert retrieved_variant.created is not None
    assert retrieved_variant.updated is not None
