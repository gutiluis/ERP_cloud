#!/bin/env python

'''
Script to test the customer model using pytest and a testing db running in docker


fixture to reuse model setup inside every test also with a session

Make sure tests has __init__.py to be recognized as a package

never use db.session in test with a session fixture

'''


import pytest
from app.models.customers import Customer
from app.extensions import db



def test_create_customer(session):
    '''Create a customer considering not nullable fields, index, max length in SQL'''
    customer = Customer(
        customer_id="Test Customer id", # watching nullable=False
        customer_name="Test customer name",
        customer_address="test_address, country zip code"
    )
    session.add(customer)
    session.commit()

    retrieved = session.query(Customer).filter_by(customer_id="Test Customer id").first()
    assert retrieved is not None
    assert retrieved.customer_name == "Test customer name"
    assert retrieved.customer_address == "test_address, country zip code"
