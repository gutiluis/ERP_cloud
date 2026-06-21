#!/usr/bin/env python3




# file: /app/auth/routes.py
# descr: admin login authentication once the adminuser and hash password is set



from flask import Blueprint, render_template, redirect, url_for, request, flash
# flask_login uses a session cookie
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models.admin_user import AdminUser


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


def authenticate_user(username, password):

    admin = db.session.execute(
        db.select(AdminUser)
        .where(AdminUser.username == username)
    ).scalar_one_or_none()

    if admin and check_password_hash(
        admin.password_hash,
        password
    ):
        return admin

    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        admin = authenticate_user(
            username,
            password
        )

        if admin:
            login_user(admin)

            next_page = request.args.get("next")
            return redirect(next_page or url_for("index.index"))

        flash("Invalid username or password", "error")

    return render_template("auth/auth_login.html")


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("auth.login")
    )
