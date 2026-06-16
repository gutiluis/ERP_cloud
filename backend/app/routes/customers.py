#!/usr/bin/env python3

# file: backend/app/routes/customers.py
'''
descr: app/models/customers.py server-rendered admin html with jinja

# TODO:
/ axios/ fetch http methods to make it admin only
even though frontend will make the transaction flask still will serialize json
list all customers /GET
# also electron admin
# api url is not a folder nor file # GET is default

[x] done
render create form /GET
[]
submit create form /POST

---
render edit form /GET

---
submit edit form /PUT # electron desktop not browser.
# browser does not support the http method in python and flask
# use react, vite, tailwind, js, fetch, ajax for the endpoint
# electron does not render html
EDIT CUSTOMER GOES IN admin/
# html forms only support get and post. browser does not support put
# react, vite, tailwind support the api endpoint with fetch
@customer_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    return jsonify({
        "updated": customer_id
    })

---
# [x] finish delete function api endpoint. missing test
delete not render/DELETE # only available in frontend js code.
# available for admin. available in electron

---
# missing /admin/src/ authentication and hide it from the frontend client

'''


from app.models import Customer
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
from app import db  # delete db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.customers import CustomerStatus, CustomerType



customer_bp = Blueprint(
    "customers", __name__,
    url_prefix="/api/admin/customers"
)


# [x] run fllask migrations always before rendering
# [x] ready without frontend
# [x] serving ready in jinja
# GET request
# use try except for db input/output only
@customer_bp.route("/")
def index_all_customers():
    "Admin render customers index/"
    # TODO: define current_user
#    if not current_user.is_admin:
#        abort(403)
    customers = Customer.query.all()
    return render_template(
        "customers/index.html",
        customers=customers
    )


@customer_bp.route("/new", methods=["GET"])
def customer_form():
    '''Admin get new customer form'''
    return render_template('customers/customer_form.html')


# in a route that only accepts post. the route is already being called from a form submission
@customer_bp.route("/new", methods=["POST"])
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
    #existing_customer = Customer.query.filter_by(
    #    customer_id=required_fields['Customer ID']
    #).first()
    #if existing_customer:
        # [ ] does not return and the db is not updating
    #    flash("Customer ID already exists.", "error")
    #    return redirect(url_for("customers.customer_form"))
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
            customer_type=CustomerType(
                request.form.get(
                "customer_type",
                "business"
                )
            )
        )
    except ValueError as error:
        current_app.logger.error(f"[LOG] Missing mandatory fields: {error}")
        return {"error": str(error)}, 400

#        flash("Invalid customer data.", "error")
#        return redirect(url_for("customers.customer_form"))
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
    except SQLAlchemyError as error:
        db.session.rollback()
        #
        current_app.logger.exception(f"Database fail: {error}")
        # flash stores message in the session. is not printing by itself
        flash("Database error. Failed to create customer.", "error")
        return redirect(url_for('customers.customer_form'))












@customer_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    '''
    Get one single customer by id from db with endpoint
    '''
    return jsonify({
        "get": customer_id
    })



# TODO: test
@customer_bp.route("/<int:customer_id>/delete")
def delete_customer(customer_id):
    '''
    only allow delete customer without invoices permamently from the db
    '''
    customer = Customer.query.get_or_404(customer_id)
    try:
        db.session.delete(customer)
        db.session.commit()
        return redirect(url_for("index"))

    except IntegrityError:
        db.session.rollback()
        # 400 is bad request client error response
        return {
            "message": "Cannot delete customer with invoices, payments, or orders"
        }, 400

    except Exception as err:
        db.session.rollback()
        print(f"[ERROR] {err}")
        # 500 is internal server error unexpected condition
        return {"message": "Unexpected error"}, 500


@customer_bp.route("/test", methods=["GET"])
def test_function():
    return current_app.name
