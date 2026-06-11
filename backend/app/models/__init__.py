#!/usr/bin/env/python3

# filename: __init__.py
'''
descr: make all folders packages
helper of 'from app import models' or import app.models
loads/exports models

'''

from app.models.user import User
from app.models.customers import Customer
from app.models.products import Product, ProductVariant
from app.models.invoice import Invoice, InvoiceItem, InvoiceTax, InvoiceStatus
from app.models.payments import Payment
from app.models.orders import Order

__all__ = [
    'User',
    'Customer',
    'Product',
    'ProductVariant',
    'Invoice',
    'InvoiceItem',
    'InvoiceStatus',
    'InvoiceTax',
    'Payment',
    'Order',
]
