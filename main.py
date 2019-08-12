#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import post, run, get, template, request, auth_basic
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

def admin_user(user, password):
    return ( user == config.get('general','admin_user') 
        and password == config.get('general','admin_password'))

# Apply
@get('/apply')
def apply():
    if request.query.get('barn') and request.query.get('vuxna'):
      return template("apply.html",
        barn=int(request.query.get('barn')),
        vuxna=int(request.query.get('vuxna')),
        kodstugor = cursor.execute("""SELECT id, namn FROM kodstugor;""").fetchall()
        )
    else:
      return template("apply_step1.html")

# Apply
@post('/apply')
def apply():
    barnid  = []
    vuxid = []
    for i, value in enumerate(request.forms.getall("barn_efternamn")):
        params = (
        request.forms.get("kodstuga").decode('utf8'),
        request.forms.getall("barn_fornamn")[i].decode('utf8'),
        request.forms.getall("barn_efternamn")[i].decode('utf8'),
        request.forms.getall("kon")[i].decode('utf8'),
        request.forms.getall("skola")[i].decode('utf8')
        )
        cursor.execute("INSERT INTO deltagare (kodstugor_id,fornamn,efternamn,kon,skola) VALUES (?,?,?,?,?)",params)
        barnid.append(cursor.execute("SELECT last_insert_rowid()").fetchone()[0])
    db.commit()
    for i, value in enumerate(request.forms.getall("vuxen_efternamn")):
        params = (
        request.forms.getall("vuxen_fornamn")[i].decode('utf8'),
        request.forms.getall("vuxen_efternamn")[i].decode('utf8'),
        request.forms.getall("email")[i].decode('utf8'),
        request.forms.getall("telefon")[i].decode('utf8')
        )
        cursor.execute("INSERT INTO kontaktpersoner (fornamn,efternamn,epost,telefon) VALUES (?,?,?,?)",params)
        vuxid.append(cursor.execute("SELECT last_insert_rowid()").fetchone()[0])
    db.commit()
    hittade = (request.forms.get("hittade").decode('utf8'),)
    cursor.execute("INSERT INTO hittade (hittade) VALUES (?)",hittade)
    db.commit()
    for vid in vuxid:
      for bid in barnid:
        cursor.execute("INSERT INTO kontaktpersoner_deltagare (kontaktpersoner_id, deltagare_id) VALUES (?,?)",(vid,bid))
    db.commit()
    for email in request.forms.getall("email"):
        send_email(email, "Tack för din intresseanmälan" , "Hej!\n\nVi har mottagit din intresseanmälan och kommer att återkomma när urvalet till kostugan är klart.\n\nMvh Kodcentrum")
    return template("apply_step2.html")

@get('/kodstugor')
@auth_basic(admin_user)
def list_kodstugor():
    if request.query.get('id'):
        id = int(request.query.get('id'))
    else:
        id = 0
    all = cursor.execute("""
        SELECT 
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text
        FROM kodstugor;
     """).fetchall();
    return template("kodstugor.html", all=all, id=id)
    
@post('/kodstugor')
@auth_basic(admin_user)
def add_uppdate_kodstuga():
    if request.forms.get("id"):
        data = (
            request.forms.get("namn").decode('utf8'),
            request.forms.get("sms_text").decode('utf8'),
            request.forms.get("epost_text").decode('utf8'),
            request.forms.get("epost_rubrik").decode('utf8'),
            request.forms.get("id").decode('utf8')
        )
        cursor.execute("""
            UPDATE kodstugor
                SET
                    namn = ?,
                    sms_text = ?,
                    epost_text = ?,
                    epost_rubrik = ?
                WHERE
                    id = ?
            """, data)
        db.commit()
    else:
        data = (
            request.forms.get("namn").decode('utf8'),
            request.forms.get("sms_text").decode('utf8'),
            request.forms.get("epost_text").decode('utf8'),
            request.forms.get("epost_rubrik").decode('utf8')
        )
        cursor.execute("""
            INSERT 
                INTO kodstugor 
                    (namn, sms_text, epost_text, epost_rubrik) 
                VALUES 
                    (?,?,?,?)
            """, data)
        db.commit()
    if request.query.get('id'):
        id = int(request.query.get('id'))
    else:
        id = 0
    all = cursor.execute("""
        SELECT 
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text
        FROM kodstugor;
     """).fetchall();
    return template("kodstugor.html", all=all, id=id)

@get('/applied')
@auth_basic(admin_user)
def listall():
    all = cursor.execute("""
        SELECT 
            kodstugor.namn,
            deltagare.id,
            deltagare.fornamn,
            deltagare.efternamn,
            deltagare.kon,
            deltagare.skola,
            kontaktpersoner.id,
            kontaktpersoner.fornamn,
            kontaktpersoner.efternamn,
            kontaktpersoner.epost,
            kontaktpersoner.telefon
        FROM deltagare
        INNER JOIN kontaktpersoner_deltagare 
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id 
        INNER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        INNER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id;
     """).fetchall();
    return template("listall.html", all=all)

run(host='localhost', port=9191)