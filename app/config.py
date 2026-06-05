import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        f"${'DATABASE_URL'}", # use the environment variable or the below line of code
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

