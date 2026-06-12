#!/usr/bin/env python3

# file: backend/app/routes/customers.py
# descr: app/models/customers.py private api

from flask import Flask, render_template, abort




@app.route("/admin/customers")
def index():
    "Render customers admin/"
    project = Project.query.all()