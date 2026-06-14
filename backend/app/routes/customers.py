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


render create form /GET
submit create form /POST

---
render edit form /GET

---
submit edit form /PUT # electron desktop not browser. browser does not support the http method in python and flask
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
delete not render/DELETE # only available in frontend js code. available for admin. available in electron

---
# missing /admin/src/ authentication and hide it from the frontend client

'''


from app.models import Customer
from flask import Blueprint, jsonify, abort, request, render_template, redirect, url_for
from app import db # delete db
from sqlalchemy import exc

customer_bp = Blueprint(
    "customers", __name__,
    url_prefix="/api/admin/customers"
)

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


@customer_bp.route("/new", methods=["POST"])
def submit_customer_form():
    '''Admin submit new customer form'''
    new_customer = Customer(
        customer_id=request.form.get('customer_id'),
        customer_name=request.form.get('customer_name'),
        customer_email=request.form.get('customer_email') or None,
        customer_phone=request.form.get('customer_phone') or None,
        customer_address=request.form.get('customer_address'),
        additional_notes=request.form.get('additional_notes') or None
    )
    db.session.add(new_customer)
    db.session.commit()
    return redirect(url_for('index'))












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
    
    
