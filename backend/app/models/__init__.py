# filename: /models/__init__.py
"""
descr: make all folders packages
helper of 'from app import models' or import app.models
loads/exports models

"""

from app.models.admin_user import AdminUser

# cart is the cart.py filename
from app.models.cart import Cart, CartItem, CartStatus
from app.models.customers import Customer
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, InvoiceTax
from app.models.orders import Order, OrderItem
from app.models.payments import Payment
from app.models.products import Product, ProductVariant
from app.models.user import User  # [info] user foreignkeyerror

__all__ = [
    "AdminUser",
    "Cart",
    "CartItem",
    "CartStatus",
    "Customer",
    "Invoice",
    "InvoiceItem",
    "InvoiceStatus",
    "InvoiceTax",
    "Order",
    "OrderItem",
    "Payment",
    "Product",
    "ProductVariant",
    "User",
]
