#!/usr/bin/env python3




# file: /app/auth/__init__.py
# descr: user_loader. logged in and anonymoususermixin. creating and configuring app



from app.extensions import login_manager
from app.models import AdminUser


# still needs login
# user_loader callback to reload the object from the user id stored in the session
# takes the str id of a user, and return the corresponding user object
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))
