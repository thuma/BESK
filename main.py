#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import post, run, get, template, request
import requests
import sqlite3
import tables
import random
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('../BESK.ini')

db = sqlite3.connect("../BESK.db")
cursor = db.cursor()

for table in tables.tables:
  db.execute(table)

def send_email(to, subject, message):
   url = config.get('general','email_url')
   json_data = {"to":to,"subject":subject,"message":message,"key":config.get('general','email_key')}
   requests.post(url, json=json_data)
# Apply
@get('/apply')
def apply():
    if request.query.get('barn') and request.query.get('vuxna'):
      return template("apply.html",
        barn=int(request.query.get('barn')),
        vuxna=int(request.query.get('vuxna')),
        kodstugor=[{"id":1,"namn":"Kodstuga1"},{"id":2,"namn":"Kodstuga2"}])
    else:
      return template("apply_step1.html")

# Apply
@post('/apply')
def apply():
    barnid  = []
    vuxid = []
    for i, value in enumerate(request.forms.getall("barn_efternamn")):
        params = (
        request.forms.get("kodstuga"),
        request.forms.getall("barn_fornamn")[i],
        request.forms.getall("barn_efternamn")[i],
        request.forms.getall("kon")[i],
        request.forms.getall("skola")[i]
        )
        barnid.append(params[0])
        cursor.execute("INSERT INTO deltagare (kodstugor_id,fornamn,efternamn,kon,skola) VALUES (?,?,?,?,?)",params)
    db.commit()
    for i, value in enumerate(request.forms.getall("vuxen_efternamn")):
        params = (
        request.forms.getall("vuxen_fornamn")[i],
        request.forms.getall("vuxen_efternamn")[i],
        request.forms.getall("email")[i],
        request.forms.getall("telefon")[i]
        )
        vuxid.append(params[0])
        cursor.execute("INSERT INTO kontaktpersoner (fornamn,efternamn,epost,telefon) VALUES (?,?,?,?)",params)
    db.commit()
    hittade = (request.forms.get("hittade"),)
    cursor.execute("INSERT INTO hittade (hittade) VALUES (?)",hittade)
    db.commit()
    for vid in vuxid:
      for bid in vuxid:
        cursor.execute("INSERT INTO kontaktpersoner_deltagare (kontaktpersoner_id, deltagare_id) VALUES (?,?)",(vid,bid))
    db.commit()
    for email in request.forms.getall("email"):
        send_email(email, "Tack för din intresseanmälan" , "Hej!\n\nVi har mottagit din intresseanmälan och kommer att återkomma när urvalet till kostugan är klart.\n\nMvh Kodcentrum")
    return template("apply_step2.html")
# Confirm
@post('/confirm')
def apply():
    return "Hello World!"

# Login
@post('/login')
def apply():
    return "Hello World!"

run(host='localhost', port=8080)