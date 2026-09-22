# filename: /backend/wsgi.py
# descr: load app from wsgi use instead of run.py for development. normal app development


from app import create_app

app = create_app()
