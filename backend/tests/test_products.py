"""
file: tests/test_products.py
descr:
Tests for the Product and ProductVariant models using pytest and the test DB.

- Use the session fixture; do not use db.session directly in tests.
"""

from decimal import Decimal

from app.models.customers import Customer
from app.models.products import Product, ProductVariant


def create_customer(session, customer_id):
    customer = Customer(
        customer_id=customer_id,
        customer_name=f"Test customer name with {customer_id}",
        customer_address="test_address, country zip code",
    )
    session.add(customer)
    session.flush()
    return customer


def test_create_product(session):
    customer = create_customer(session, "Customer-001")

    product = Product(
        product_id="PID-001",
        product_name="Test Product",
        customer_id=customer.customer_id,
        brand="TestBrand",
        category="Electronics",
        description="A test product description.",
    )
    session.add(product)
    session.commit()

    retrieved = session.query(Product).filter_by(product_id="PID-001").first()

    assert retrieved is not None
    assert retrieved.product_name == "Test Product"
    assert retrieved.product_id == "PID-001"
    assert retrieved.customer_id == customer.customer_id
    assert retrieved.brand == "TestBrand"
    assert retrieved.category == "Electronics"
    assert retrieved.description == "A test product description."
    assert retrieved.is_active is True
    assert retrieved.url is None
    assert retrieved.url_tag is None
    assert retrieved.additional_notes is None


def test_create_product_with_optionals(session):
    customer = create_customer(session, "Customer-002")

    product = Product(
        product_id="PID-002",
        product_name="Product With URL",
        customer_id=customer.customer_id,
        brand="Brand",
        category="Category",
        description="Description",
        url="https://example.com/product-with-url",
        url_tag="tag",
        additional_notes="Some notes",
    )
    session.add(product)
    session.commit()

    retrieved = session.query(Product).filter_by(product_id="PID-002").first()

    assert retrieved is not None
    assert retrieved.url == "https://example.com/product-with-url"
    assert retrieved.url_tag == "tag"
    assert retrieved.additional_notes == "Some notes"


def test_create_product_variant(session):
    customer = create_customer(session, "Customer-003")

    product = Product(
        product_id="PID-003",
        product_name="Parent Product",
        customer_id=customer.customer_id,
        brand="Brand",
        category="Category",
        description="Description",
    )
    session.add(product)
    session.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku="SKU-003",
        price=Decimal("19.99"),
        stock_quantity=100,
        color="Blue",
        size="M",
    )
    session.add(variant)
    session.commit()

    retrieved = session.query(ProductVariant).filter_by(sku="SKU-003").first()

    assert retrieved is not None
    assert retrieved.product_id == product.id
    assert retrieved.sku == "SKU-003"
    assert retrieved.price == Decimal("19.99")
    assert retrieved.stock_quantity == 100
    assert retrieved.color == "Blue"
    assert retrieved.size == "M"
    assert retrieved.is_active is True
    assert retrieved.is_in_stock is True
    assert retrieved.product is not None
    assert retrieved.product.product_id == "PID-003"


def test_product_children_variants_relationship(session):
    customer = create_customer(session, "Customer-004")

    product = Product(
        product_id="PID-004",
        product_name="Product With Variants",
        customer_id=customer.customer_id,
        brand="Brand",
        category="Category",
        description="Description",
    )
    session.add(product)
    session.flush()

    v1 = ProductVariant(
        product_id=product.id,
        sku="SKU-004-A",
        price=Decimal("10.00"),
        stock_quantity=5,
    )
    v2 = ProductVariant(
        product_id=product.id,
        sku="SKU-004-B",
        price=Decimal("20.00"),
        stock_quantity=10,
    )

    session.add_all([v1, v2])
    session.commit()

    retrieved = session.query(Product).filter_by(product_id="PID-004").first()

    assert retrieved is not None
    assert len(retrieved.variants) == 2

    prices = {variant.price for variant in retrieved.variants}
    assert prices == {Decimal("10.00"), Decimal("20.00")}

    assert v1.is_in_stock is True
    assert v2.is_in_stock is True


def test_product_and_variant_timestamps(session):
    customer = create_customer(session, "Customer-005")

    product = Product(
        product_id="PID-005",
        product_name="Timestamp Product",
        customer_id=customer.customer_id,
        brand="Brand",
        category="Category",
        description="Description",
    )
    session.add(product)
    session.flush()

    assert product.created is not None
    assert product.updated is not None

    variant = ProductVariant(
        product_id=product.id,
        sku="SKU-005",
        price=Decimal("1.00"),
        stock_quantity=0,
    )
    session.add(variant)
    session.commit()

    retrieved_variant = session.query(ProductVariant).filter_by(sku="SKU-005").first()

    assert retrieved_variant is not None
    assert retrieved_variant.created is not None
    assert retrieved_variant.updated is not None


def test_public_products(client, session):
    customer = create_customer(session, "Customer-PUBLIC-001")

    product = Product(
        product_id="PID-PUBLIC-001",
        product_name="Public Test Product",
        customer_id=customer.customer_id,
        brand="PublicBrand",
        category="Electronics",
        description="A public product.",
    )
    session.add(product)
    session.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku="SKU-PUBLIC-001",
        price=Decimal("29.99"),
        stock_quantity=10,
        color="Black",
        size="M",
        is_active=True,
    )
    session.add(variant)
    session.commit()

    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.get_json()

    assert "products" in data
    assert len(data["products"]) == 1

    public_product = data["products"][0]

    assert public_product["product_id"] == "PID-PUBLIC-001"
    assert public_product["product_name"] == "Public Test Product"
    assert public_product["brand"] == "PublicBrand"
    assert public_product["category"] == "Electronics"
    assert public_product["description"] == "A public product."

    assert len(public_product["variants"]) == 1

    public_variant = public_product["variants"][0]

    assert public_variant["sku"] == "SKU-PUBLIC-001"
    assert public_variant["price"] == "29.99"
    assert public_variant["stock_quantity"] == 10
    assert public_variant["color"] == "Black"
    assert public_variant["size"] == "M"
    assert public_variant["is_in_stock"] is True


def test_public_products_excludes_inactive_products(client, session):
    customer = create_customer(session, "Customer-PUBLIC-002")

    active_product = Product(
        product_id="PID-PUBLIC-ACTIVE",
        product_name="Active Product",
        customer_id=customer.customer_id,
        brand="Brand",
        category="Category",
        description="Active product.",
        is_active=True,
    )

    inactive_product = Product(
        product_id="PID-PUBLIC-INACTIVE",
        product_name="Inactive Product",
        customer_id=customer.customer_id,
        brand="Brand",
        category="Category",
        description="Inactive product.",
        is_active=False,
    )

    session.add_all([active_product, inactive_product])
    session.commit()

    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.get_json()

    product_ids = {product["product_id"] for product in data["products"]}

    assert "PID-PUBLIC-ACTIVE" in product_ids
    assert "PID-PUBLIC-INACTIVE" not in product_ids


def test_public_products_excludes_inactive_variants(client, session):
    customer = create_customer(session, "Customer-PUBLIC-003")

    product = Product(
        product_id="PID-PUBLIC-VARIANTS",
        product_name="Variant Test Product",
        customer_id=customer.customer_id,
        brand="Brand",
        category="Category",
        description="Variant test product.",
    )

    session.add(product)
    session.flush()

    active_variant = ProductVariant(
        product_id=product.id,
        sku="SKU-PUBLIC-ACTIVE",
        price=Decimal("10.00"),
        stock_quantity=5,
        is_active=True,
    )

    inactive_variant = ProductVariant(
        product_id=product.id,
        sku="SKU-PUBLIC-INACTIVE",
        price=Decimal("20.00"),
        stock_quantity=5,
        is_active=False,
    )

    session.add_all([active_variant, inactive_variant])
    session.commit()

    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.get_json()

    public_product = data["products"][0]

    variant_skus = {variant["sku"] for variant in public_product["variants"]}

    assert "SKU-PUBLIC-ACTIVE" in variant_skus
    assert "SKU-PUBLIC-INACTIVE" not in variant_skus


def test_public_products_requires_no_authentication(client, session):
    response = client.get("/api/products")

    assert response.status_code == 200

    def test_public_products_empty_catalog(client):
        response = client.get("/api/products")

        assert response.status_code == 200
        assert response.get_json() == {"products": []}
