# file: backend/app/config.py
# descr: load flask flash secret key, and flask_login secret key

import os

from dotenv import load_dotenv

load_dotenv()
# construct a predictable filesystem location for sqlite database/backup
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base Flask configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET") or ""
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY") or ""
    STRIPE_SUCCESS_URL = os.environ.get("STRIPE_SUCCESS_URL") or ""
    STRIPE_CANCEL_URL = os.environ.get("STRIPE_CANCEL_URL") or ""
    TRUSTED_HOSTS = [
        host.strip() for host in os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
    ]

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")


class TestConfig(Config):
    """Pytest configuration."""

    TESTING = True
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite://"


class ProductionConfig(Config):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or ""
    SQLITE_BACKUP_PATH = os.environ.get(
        "SQLITE_BACKUP_PATH",
        os.path.join(basedir, "data-production-backup.sqlite"),
    )


config = {
    "default": Config,
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "production": ProductionConfig,
}
