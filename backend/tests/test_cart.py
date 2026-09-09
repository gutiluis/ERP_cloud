# file: test_cart.py
# descr: cart test file with erp_test mysql db

from uuid import uuid4
from decimal import Decimal

from app.models.products import Product, ProductVariant
from app.models.cart import Cart, CartStatus
from app.models.customers import Customer


def test_create_cart(client, cart_product_variant):
    customer, product, variant = cart_product_variant

    response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Cart created successfully."
    assert data["cart_token"]

    cart = Cart.query.filter_by(cart_token=data["cart_token"]).first()

    assert cart is not None
    assert cart.customer_id == customer.id
    assert cart.total_amount == Decimal("50.00")

    assert len(cart.items) == 1
    assert cart.items[0].product_id == product.id
    assert cart.items[0].product_variant_id == variant.id
    assert cart.items[0].quantity == 2
    assert cart.items[0].unit_price == Decimal("25.00")


def test_create_cart_insufficient_stock(client, cart_product_variant):
    # conftest.py has customer, product and variant under cart_product_variant
    # unpack the value returned by the fixture. not function parameters
    _, _, variant = cart_product_variant

    response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 11,
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Insufficient stock"}

    assert Cart.query.count() == 0


def test_create_cart_inactive_variant(client, cart_product_variant):
    _, _, variant = cart_product_variant

    variant.is_active = False

    response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Product variant not found"}

    assert Cart.query.count() == 0


def test_create_cart_missing_product_variant_id(client):
    response = client.post(
        "/api/cart",
        json={"quantity": 1},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "product_variant_id is required"}

    assert Cart.query.count() == 0


def test_create_cart_invalid_quantity(client, cart_product_variant):
    _, _, variant = cart_product_variant

    for quantity in (0, -1):
        response = client.post(
            "/api/cart",
            json={
                "product_variant_id": variant.id,
                "quantity": quantity,
            },
        )

        assert response.status_code == 400
        assert response.get_json() == {"error": "quantity must be greater than zero"}

    assert Cart.query.count() == 0


def test_create_cart_variant_not_found(client):
    response = client.post(
        "/api/cart",
        json={
            "product_variant_id": 999999,
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Product variant not found"}

    assert Cart.query.count() == 0


def test_get_cart(client, cart_product_variant):
    _, product, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201

    cart_token = create_response.get_json()["cart_token"]

    response = client.get(f"/api/cart/{cart_token}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["cart_token"] == cart_token
    assert data["total_amount"] == "50.00"

    assert len(data["items"]) == 1

    item = data["items"][0]

    assert item["product_id"] == product.id
    assert item["product_variant_id"] == variant.id
    assert item["quantity"] == 2
    assert item["unit_price"] == "25.00"


def test_get_cart_not_found(client):
    """
    Retrieve a cart using an invalid token
    """
    response = client.get("/api/cart/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_add_item(client, cart_product_variant, session):
    """
    After the cart is created with the first item, the buyer needs to add additional variants
    """
    customer, product, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201

    cart_token = create_response.get_json()["cart_token"]

    second_variant = ProductVariant(
        product_id=product.id,
        is_active=True,
        price=Decimal("15.00"),
        stock_quantity=5,
        sku="CART-TEST-SKU-002",
    )

    session.add(second_variant)
    session.flush()

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": second_variant.id,
            "quantity": 2,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["cart_token"] == cart_token
    assert data["item"]["product_variant_id"] == second_variant.id
    assert data["item"]["quantity"] == 2
    assert data["item"]["unit_price"] == "15.00"
    assert data["total_amount"] == "80.00"


def test_add_existing_item_increases_quantity(
    client,
    cart_product_variant,
):
    """
    Cart can accept a second variant and correctly recalculate its total.
    Adding the same variant should increase its quantity, not create a second CartItem
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201

    cart_token = create_response.get_json()["cart_token"]

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": variant.id,
            "quantity": 3,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["item"]["product_variant_id"] == variant.id
    assert data["item"]["quantity"] == 5
    assert data["item"]["unit_price"] == "25.00"
    assert data["total_amount"] == "125.00"

    cart_response = client.get(f"/api/cart/{cart_token}")

    assert len(cart_response.get_json()["items"]) == 1


def test_add_item_different_seller(client, cart_product_variant, session):
    _, _, variant_a = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={"product_variant_id": variant_a.id, "quantity": 1},
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    customer_b = Customer(
        customer_id="customer_cart_002",
        customer_name="Cart Test Customer 2",
        customer_email="cart_test_2@example.com",
    )

    product_b = Product(
        product_id="product_cart_002",
        product_name="Cart Test Product 2",
        customer_id=customer_b.customer_id,
        brand="Test Brand",
        category="Test Category",
        description="Cart test product 2",
    )

    session.add_all([customer_b, product_b])
    session.flush()

    variant_b = ProductVariant(
        product_id=product_b.id,
        is_active=True,
        price=Decimal("15.00"),
        stock_quantity=5,
        sku="CART-TEST-SKU-002",
    )

    session.add(variant_b)
    session.flush()

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": variant_b.id,
            "quantity": 1,
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Product does not belong to this seller"}

    cart_response = client.get(f"/api/cart/{cart_token}")
    data = cart_response.get_json()

    assert len(data["items"]) == 1
    assert data["items"][0]["product_variant_id"] == variant_a.id
    assert data["items"][0]["quantity"] == 1
    assert data["total_amount"] == "25.00"


def test_add_item_insufficient_stock(client, cart_product_variant):
    """
    Infufficient stock when adding an item to an existing cart
    if the cart already contains
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={"product_variant_id": variant.id, "quantity": 1},
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": variant.id,
            "quantity": 10,
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Insufficient stock"}

    cart_response = client.get(f"/api/cart/{cart_token}")
    data = cart_response.get_json()

    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 1
    assert data["total_amount"] == "25.00"


def test_add_item_inactive_variant(client, cart_product_variant, session):
    """
    inactive variant cannot be added to an existing cart.

    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={"product_variant_id": variant.id, "quantity": 1},
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    variant.is_active = False
    session.flush()

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Product variant not found"}

    cart_response = client.get(f"/api/cart/{cart_token}")
    data = cart_response.get_json()

    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 1
    assert data["total_amount"] == "25.00"


def test_add_item_variant_not_found(client, cart_product_variant):
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={"product_variant_id": variant.id, "quantity": 1},
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": 999999,
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Product variant not found"}

    cart_response = client.get(f"/api/cart/{cart_token}")
    data = cart_response.get_json()

    assert len(data["items"]) == 1
    assert data["items"][0]["product_variant_id"] == variant.id
    assert data["items"][0]["quantity"] == 1
    assert data["total_amount"] == "25.00"


def test_add_item_missing_product_variant_id(client, cart_product_variant):
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={"product_variant_id": variant.id, "quantity": 1},
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={"quantity": 1},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "product_variant_id is required"}


def test_add_item_missing_quantity(client, cart_product_variant):
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={"product_variant_id": variant.id, "quantity": 1},
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={"product_variant_id": variant.id},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "quantity must be greater than zero"}


def test_add_item_invalid_quantity(client, cart_product_variant):
    """
    verify 0 and negative quantities are rejected
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={"product_variant_id": variant.id, "quantity": 1},
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    for quantity in (0, -1):
        response = client.post(
            f"/api/cart/{cart_token}/items",
            json={
                "product_variant_id": variant.id,
                "quantity": quantity,
            },
        )

        assert response.status_code == 400
        assert response.get_json() == {"error": "quantity must be greater than zero"}


def test_add_item_cart_not_found(client, cart_product_variant):
    """
    Forbit an item when the supplied cart_token doesn't correspond to an existing cart
    """
    _, _, variant = cart_product_variant

    response = client.post(
        "/api/cart/nonexistent-cart-token/items",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert response.status_code == 404


def test_add_item_uses_variant_price(client, cart_product_variant, session):
    """
    Cart total when adding a new variant and make sure the persistet CartItem has the authoritative db price
    """
    _, product, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    second_variant = ProductVariant(
        product_id=product.id,
        is_active=True,
        price=Decimal("15.00"),
        stock_quantity=10,
        sku="CART-TEST-SKU-003",
    )

    session.add(second_variant)
    session.flush()

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": second_variant.id,
            "quantity": 2,
            "unit_price": "9999.99",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["item"]["unit_price"] == "15.00"
    assert data["total_amount"] == "55.00"


def test_add_item_exact_stock_limit(client, cart_product_variant, session):
    """
    Adding an item whose quantity exactly equals the available stock
    """
    _, product, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": variant.id,
            "quantity": 9,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["item"]["quantity"] == 10
    assert data["item"]["unit_price"] == "25.00"
    assert data["total_amount"] == "250.00"


def test_get_cart_multiple_items(client, cart_product_variant, session):
    """
    Cart containing multiple items returns all items correctly and calculates the total correctly
    """
    _, product, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    second_variant = ProductVariant(
        product_id=product.id,
        is_active=True,
        price=Decimal("15.00"),
        stock_quantity=10,
        sku="CART-TEST-SKU-004",
    )

    session.add(second_variant)
    session.flush()

    add_response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": second_variant.id,
            "quantity": 3,
        },
    )

    assert add_response.status_code == 201

    response = client.get(f"/api/cart/{cart_token}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["cart_token"] == cart_token
    assert data["total_amount"] == "95.00"
    assert len(data["items"]) == 2

    items = {item["product_variant_id"]: item for item in data["items"]}

    assert items[variant.id]["quantity"] == 2
    assert items[variant.id]["unit_price"] == "25.00"

    assert items[second_variant.id]["quantity"] == 3
    assert items[second_variant.id]["unit_price"] == "15.00"


def test_get_empty_cart(client, cart_product_variant, session):
    """
    GET /api/cart/<cart_token>
    Existing cart with no items is handled correctly
    """
    customer, _, _ = cart_product_variant

    cart = Cart(
        cart_token=str(uuid4()),
        customer_id=customer.id,
        total_amount=Decimal("0.00"),
    )

    session.add(cart)
    session.commit()

    response = client.get(f"/api/cart/{cart.cart_token}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["cart_token"] == cart.cart_token
    assert data["items"] == []
    assert data["total_amount"] == "0.00"


def test_get_cart_not_found_response(client):
    """
    GET /api/cart/cart_token
    """
    response = client.get("/api/cart/nonexistent-cart-token")

    assert response.status_code == 404


def test_update_item_quantity(client, cart_product_variant):
    """
    /api/cart/cart_token/items/item_id
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201

    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")
    item_id = cart_response.get_json()["items"][0]["id"]

    response = client.patch(
        f"/api/cart/{cart_token}/items/{item_id}",
        json={"quantity": 5},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["item"]["id"] == item_id
    assert data["item"]["quantity"] == 5
    assert data["item"]["unit_price"] == "25.00"
    assert data["total_amount"] == "125.00"


def test_update_item_invalid_quantity(client, cart_product_variant):
    """
    Test that 0 and negative quantities are rejected
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")
    item_id = cart_response.get_json()["items"][0]["id"]

    for quantity in (0, -1):
        response = client.patch(
            f"/api/cart/{cart_token}/items/{item_id}",
            json={"quantity": quantity},
        )

        assert response.status_code == 400
        assert response.get_json() == {"error": "quantity must be greater than zero"}


def test_update_item_insufficient_stock(client, cart_product_variant):
    """
    Test patch stock limit updating api endpoint.
    Verify that setting the quantity above the variant's available stock is rejected and the existing quantity remains unchanged
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")
    item_id = cart_response.get_json()["items"][0]["id"]

    response = client.patch(
        f"/api/cart/{cart_token}/items/{item_id}",
        json={"quantity": 11},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Insufficient stock"}

    cart_response = client.get(f"/api/cart/{cart_token}")
    data = cart_response.get_json()

    assert data["items"][0]["quantity"] == 2
    assert data["total_amount"] == "50.00"


def test_update_item_not_found(client, cart_product_variant):
    """
    PATCH update method with non-existent-cart-item
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    response = client.patch(
        f"/api/cart/{cart_token}/items/999999",
        json={"quantity": 2},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Cart item not found"}


def test_update_item_missing_quantity(client, cart_product_variant):
    """
    PATCH update missing quantity case
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")
    item_id = cart_response.get_json()["items"][0]["id"]

    response = client.patch(
        f"/api/cart/{cart_token}/items/{item_id}",
        json={},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "quantity must be greater than zero"}


def test_update_item_from_different_cart(client, cart_product_variant):
    """
    Item from cart a cannot be modified through cart b's token
    """
    _, _, variant = cart_product_variant

    first_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    second_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    cart_token_a = first_response.get_json()["cart_token"]
    cart_token_b = second_response.get_json()["cart_token"]

    cart_a = client.get(f"/api/cart/{cart_token_a}").get_json()
    item_id = cart_a["items"][0]["id"]

    response = client.patch(
        f"/api/cart/{cart_token_b}/items/{item_id}",
        json={"quantity": 5},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Cart item not found"}

    cart_a = client.get(f"/api/cart/{cart_token_a}").get_json()
    cart_b = client.get(f"/api/cart/{cart_token_b}").get_json()

    assert cart_a["items"][0]["quantity"] == 1
    assert cart_a["total_amount"] == "25.00"

    assert cart_b["items"][0]["quantity"] == 2
    assert cart_b["total_amount"] == "50.00"


def test_update_item_exact_stock_limit(client, cart_product_variant):
    """
    PATCH update
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")
    item_id = cart_response.get_json()["items"][0]["id"]

    response = client.patch(
        f"/api/cart/{cart_token}/items/{item_id}",
        json={"quantity": 10},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["item"]["quantity"] == 10
    assert data["item"]["unit_price"] == "25.00"
    assert data["total_amount"] == "250.00"


def test_delete_item(client, cart_product_variant):
    """
    Delete the only item should leave the cart empty and reset the total to 0.00
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")
    item_id = cart_response.get_json()["items"][0]["id"]

    response = client.delete(f"/api/cart/{cart_token}/items/{item_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["cart_token"] == cart_token
    assert data["total_amount"] == "0.00"

    cart_response = client.get(f"/api/cart/{cart_token}")

    data = cart_response.get_json()

    assert data["items"] == []
    assert data["total_amount"] == "0.00"


def test_delete_item_not_found(client, cart_product_variant):
    """
    Delete non existent cart item
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    response = client.delete(f"/api/cart/{cart_token}/items/999999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Cart item not found"}


def test_delete_item_from_different_cart(client, cart_product_variant):
    """
    Item belonging to Cart A cannot be deleted usin Cart B's token.
    Item must belong to the cart identifier by the cart_token
    """
    _, _, variant = cart_product_variant

    first_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    second_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    cart_token_a = first_response.get_json()["cart_token"]
    cart_token_b = second_response.get_json()["cart_token"]

    cart_a = client.get(f"/api/cart/{cart_token_a}").get_json()
    item_id = cart_a["items"][0]["id"]

    response = client.delete(f"/api/cart/{cart_token_b}/items/{item_id}")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Cart item not found"}

    cart_a = client.get(f"/api/cart/{cart_token_a}").get_json()
    cart_b = client.get(f"/api/cart/{cart_token_b}").get_json()

    assert len(cart_a["items"]) == 1
    assert cart_a["items"][0]["quantity"] == 1
    assert cart_a["total_amount"] == "25.00"

    assert len(cart_b["items"]) == 1
    assert cart_b["items"][0]["quantity"] == 2
    assert cart_b["total_amount"] == "50.00"


def test_delete_one_of_multiple_items(client, cart_product_variant, session):
    """
    Delete with multiple items.
    Deleting one item doesn't automatically remove the other items or calculate the total incorrectly
    """
    _, product, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 2,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    second_variant = ProductVariant(
        product_id=product.id,
        is_active=True,
        price=Decimal("15.00"),
        stock_quantity=10,
        sku="CART-TEST-SKU-005",
    )

    session.add(second_variant)
    session.flush()

    add_response = client.post(
        f"/api/cart/{cart_token}/items",
        json={
            "product_variant_id": second_variant.id,
            "quantity": 3,
        },
    )

    assert add_response.status_code == 201

    cart_response = client.get(f"/api/cart/{cart_token}")

    data = cart_response.get_json()

    assert len(data["items"]) == 2
    assert data["total_amount"] == "95.00"

    first_item_id = next(
        item["id"] for item in data["items"] if item["product_variant_id"] == variant.id
    )

    response = client.delete(f"/api/cart/{cart_token}/items/{first_item_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["total_amount"] == "45.00"

    cart_response = client.get(f"/api/cart/{cart_token}")

    data = cart_response.get_json()

    assert len(data["items"]) == 1
    assert data["items"][0]["product_variant_id"] == second_variant.id
    assert data["items"][0]["quantity"] == 3
    assert data["total_amount"] == "45.00"


def test_create_cart_pending_status(
    client,
    cart_product_variant,
    session,
):
    """
    Cart created by the API starts in the corect state-pending
    """
    _, _, variant = cart_product_variant

    response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert response.status_code == 201

    cart_token = response.get_json()["cart_token"]

    cart = Cart.query.filter_by(cart_token=cart_token).first()

    assert cart is not None
    assert cart.status == CartStatus.PENDING


def test_delete_item_already_deleted(client, cart_product_variant):
    """
    Delete on an empty cart return 404
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")

    item_id = cart_response.get_json()["items"][0]["id"]

    response = client.delete(f"/api/cart/{cart_token}/items/{item_id}")

    assert response.status_code == 200

    response = client.delete(f"/api/cart/{cart_token}/items/{item_id}")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Cart item not found"}


def test_update_item_reduce_quantity(client, cart_product_variant):
    """
    Patch with the exact stock boundary in the opposite direction. start with the maximum quantity and reduce it
    """
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 10,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")

    item_id = cart_response.get_json()["items"][0]["id"]

    response = client.patch(
        f"/api/cart/{cart_token}/items/{item_id}",
        json={"quantity": 3},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["item"]["quantity"] == 3
    assert data["item"]["unit_price"] == "25.00"
    assert data["total_amount"] == "75.00"


def test_update_item_cart_not_found(client):
    """
    Patch when the cart doesn't exist
    """
    response = client.patch(
        "/api/cart/nonexistent-cart-token/items/1",
        json={"quantity": 2},
    )

    assert response.status_code == 404


def test_update_item_inactive_variant(client, cart_product_variant, session):
    _, _, variant = cart_product_variant

    create_response = client.post(
        "/api/cart",
        json={
            "product_variant_id": variant.id,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201
    cart_token = create_response.get_json()["cart_token"]

    cart_response = client.get(f"/api/cart/{cart_token}")

    item_id = cart_response.get_json()["items"][0]["id"]

    variant.is_active = False
    session.flush()

    response = client.patch(
        f"/api/cart/{cart_token}/items/{item_id}",
        json={"quantity": 2},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Product variant not found"}

    cart_response = client.get(f"/api/cart/{cart_token}")

    data = cart_response.get_json()

    assert data["items"][0]["quantity"] == 1
    assert data["total_amount"] == "25.00"
