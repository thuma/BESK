#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import post, run, get, static_file
import requests
import sqlite3
import tables

db = sqlite3.connect("../BESK.db").cursor()

for table in tables.tables:
  db.execute(table)

# Serve index.html in dev mode:
@get("/index.html>")
def main():
    return static_file("index.html",root="")
@get("/")
def main():
    return static_file("index.html",root="")

# Apply
@post('/apply')
def apply():
    return "Hello World!"

# Confirm
@post('/confirm')
def apply():
    return "Hello World!"

# Login
@post('/login')
def apply():
    return "Hello World!"

run(host='localhost', port=8080)