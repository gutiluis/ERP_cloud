# file: backend/app/config.py
# descr: load flask flash secret key, and flask_login secret key


import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # os.getenv returns none if missing
    # change to os.environ in production
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-key")
    # os.environ crashes immediately
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # change to os.environ for production
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL")
    STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL")


class TestConfig(Config):
    """Pytest"""

    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")
