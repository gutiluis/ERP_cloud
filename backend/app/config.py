#!/usr/bin/env python3

# file:
# descr:



from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        f"{'DATABASE_URL'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

