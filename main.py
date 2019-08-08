#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import post, run, get, template
import requests
import sqlite3
import tables

db = sqlite3.connect("../BESK.db").cursor()

for table in tables.tables:
  db.execute(table)

# Apply
@get('/apply')
def apply():
    return template("apply.html")

# Apply
@post('/apply')
def apply():
    return template("apply.html")

# Confirm
@post('/confirm')
def apply():
    return "Hello World!"

# Login
@post('/login')
def apply():
    return "Hello World!"

run(host='localhost', port=8080, reloader=True)