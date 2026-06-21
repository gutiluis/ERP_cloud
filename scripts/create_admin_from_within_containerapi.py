#!/usr/bin/env python3


# file: /scripts/create_admin_from_within_containerapi.py
# descr: insert an admin with password hash from the model




from app import db
from app.models.admin_user import AdminUser
from werkzeug.security import generate_password_hash

admin = AdminUser(
    admin_id="admin-1",
    username="admin",
    password_hash=generate_password_hash("your_password")
)

db.session.add(admin)
db.session.commit()
