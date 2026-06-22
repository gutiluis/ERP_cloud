#!/usr/bin/env python3

# file: backend/app/routes/customers.py
'''
descr: app/models/customers.py server-rendered admin html with jinja

# api url is not a folder nor file # GET is default

'''

from app.extensions import current_user, login_required
from app.models import Customer
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, abort
from app import db  # delete db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.customers import CustomerStatus, CustomerType



customer_bp = Blueprint(
    "customers", __name__,
    url_prefix="/api/admin/customers"
)

# use try except for db input/output only
@customer_bp.route("/")
@login_required
def index_all_customers():
    """
    Admin render all customers
    """
    # TODO: define current_user
    # pytest
    # authentication and hide it from the client
    # to use is_authenticated you need is_authenticated you need UserMixin
#    if not current_user.is_authenticated and current_user.is_active:
#        abort(403)
    customers = db.session.execute(db.select(Customer).order_by(Customer.customer_id)).scalars().all()
    return render_template(
        "customers/index.html",
        customers=customers
    )


@customer_bp.route("/new", methods=["GET"])
@login_required
def customer_form():
    '''Admin get new customer form'''
    return render_template('customers/customer_form.html')


# [ ] missing phone filter
# in a route that only accepts post. the route is already being called from a form submission
@customer_bp.route("/new", methods=["POST"])
@login_required
def submit_customer_form():
    '''Admin submit new customer form with redirection'''
    # required_fields dictionary are nullable=False inside the class model
    required_fields = {
        "Customer ID": request.form.get('customer_id', '').strip(),
        "Customer Name": request.form.get('customer_name', '').strip(),
        "Customer Status": request.form.get('customer_status', '').strip(),
    }
    # empty customer_status exists and exits here
    for field_name, value in required_fields.items():
        if not value:
            # under set-cookie in base64-encoded json through a session cookie
            flash(f"{field_name} is required.", "error")
            return redirect(url_for('customers.customer_form'))
    try:
        new_customer = Customer(
            customer_id=required_fields["Customer ID"],
            customer_name=required_fields["Customer Name"],
            # sqlalchemy stores python none as sql null
            customer_email=request.form.get(
                'customer_email', ''
                ).strip().lower() or None,
            customer_phone=request.form.get(
                'customer_phone', ''
                ).strip() or None,
            customer_address=request.form.get(
                'customer_address', ''
                ).strip() or None,
            additional_notes=request.form.get(
                'additional_notes', ''
                ).strip() or None,
            customer_status=CustomerStatus(
                required_fields[
                    'Customer Status']
            ),
            # nullable=False in the model
            customer_type=CustomerType(
                request.form.get(
                "customer_type",
                "business"
                )
            )
        )
    # won't be reached being caught after the required_fields statement
    except ValueError as error:
        flash("Invalid customer data.", "error")
        return redirect(url_for("customers.customer_form"))
    try:
        db.session.add(new_customer)
        db.session.commit()
        # [ x ] the flash is visible in the customer_form
        flash("Customer creaded successfully", "success")
        return redirect(url_for("customers.customer_form"))
    # exception for repeated customer_id, customer_name, customer_email unique=True
    except IntegrityError as error: # duplicate check with customer_id
        db.session.rollback()
        # current_app is for dev producton logs. the user does not see it
        current_app.logger.error(f"[LOG] Customer has same customer_id, or same customer_name or same email: {error}")
        # [ x ] redirect template after creating a customer to the page. 
        # [ x ] flash is being rendered in the customer_form.html
        flash("Customer ID already exists. Failed to create customer", "error")
        return redirect(url_for("customers.customer_form"))
    # integrityrror is a sublass of sqlalchemyerror
    except SQLAlchemyError as error:
        db.session.rollback()
        #
        current_app.logger.exception(f"Database fail: {error}")
        # flash stores message in the session. is not printing by itself
        flash("Database error. Failed to create customer.", "error")
        return redirect(url_for('customers.customer_form'))


# [ x ] ready rest api endpoint
@customer_bp.route("/edit/<string:customer_id>", methods=["GET"])
@login_required
def edit_customer(customer_id):
    '''Admin customer edit form fetch'''
    # query.get_or_404 by primary_key only not string customer_id
    customer = Customer.query.filter_by(customer_id=customer_id).one_or_404()
    return render_template("customers/editcustomer.html", customer=customer)


# html does not accept put
# REST or RESTful
# <int:custmer_id> only accepts integers customer_id is a string. id is the other option with straight db primary_key
# frontend fetch/ajax method is put. not available with flask
@customer_bp.route("/edit/<string:customer_id>", methods=["POST"])
@login_required
def update_customer(customer_id):
    '''Admin update customer form'''
    customer = Customer.query.filter_by(customer_id=customer_id).one_or_404()
    if request.method == "POST":
    # customer_id is the variable # customer is the model
        customer.customer_id = request.form.get("customer_id")
        customer.customer_name = request.form.get("customer_name")
        customer.customer_email = request.form.get("customer_email")
        customer.customer_phone = request.form.get("customer_phone")
        customer.customer_address = request.form.get("customer_address")
        customer.additional_notes = request.form.get("additional_notes")
        customer.customer_status = request.form.get("customer_status")
        customer.customer_type = request.form.get("customer_type")
        db.session.commit()
    # return {"message", "customer updated"} # creates a set not json
        return redirect(url_for('customers.index_all_customers'))
    return render_template("customers/editcustomer.html")


@customer_bp.route("/<string:customer_id>", methods=["GET"])
@login_required
def customer_detail(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).one_or_404()
    return render_template("customers/customerdetail.html", customer=customer)


# TODO: test
@customer_bp.route("/<string:customer_id>/delete")
@login_required
def delete_customer(customer_id):
    '''
    only allow delete customer without invoices permamently from the db
    '''
    customer = Customer.query.filter_by(customer_id=customer_id).one_or_404()
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for("customers.index_all_customers"))

