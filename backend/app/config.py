#!/usr/bin/env python3

# file: backend/app/config.py
# descr: load flask flash secret key, and flask_login secret key



from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    # os.getenv returns none if missing
    # change to os.environ in production
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-key")
    # os.environ crashes immediately
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

