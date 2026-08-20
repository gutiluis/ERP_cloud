# file: /backend/app/extensions.py
# descr: flask extensions

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# LoginManager is extension object not configuration data
login_manager = LoginManager()
login_manager.login_view = "auth.login"


migrate = Migrate()
