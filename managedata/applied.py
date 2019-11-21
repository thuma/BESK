#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db, texter
from tools import send_email, read_post_data
import uuid
import json
import phonenumbers
import time
from gevent import spawn

def new(request, response):
    data_to_db = {
        "kids":[],
        "adults":[]
        }
    formdata = read_post_data(request)
    if "approve" not in formdata:
        response('400 Bad Request', [('Content-Type', 'text/html')])
        return bytes("Du måste acceptera Kodcentrums Integritetspolicy.",'utf-8')
    try:
        kodstugaid = formdata["kodstuga"][0]
        kodstuga = db.cursor.execute("""
            SELECT namn
            FROM kodstugor WHERE id = ?;
        """,(kodstugaid,)).fetchall()[0][0]
    except:
        response('400 Bad Request', [('Content-Type', 'text/html')])
        return bytes("Välj en kodstuga.",'utf-8')
    now = int(time.time())

    for i, value in enumerate(formdata["barn_efternamn"]):
        if formdata["barn_fornamn"][i] == "":
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i förnamn för samtliga barn.",'utf-8')
        if formdata["barn_efternamn"][i] == "":
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i efternamn för samtliga barn.",'utf-8')
        if formdata["kon"][i] == "":
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i kön för samtliga barn.",'utf-8')
        if formdata["klass"][i] == "":
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i klass för samtliga barn.",'utf-8')
        if formdata["skola"][i] == "":
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i skola för samtliga barn.",'utf-8')
        data_to_db["kids"].append(
            (
            uuid.uuid4().hex,
            kodstugaid,
            formdata["barn_fornamn"][i],
            formdata["barn_efternamn"][i],
            formdata["kon"][i],
            formdata["klass"][i],
            formdata["skola"][i],
            now,
            "ansökt"
            )
        )

    for i, value in enumerate(formdata["vuxen_efternamn"]):
        try:
            phone_number= phonenumbers.parse(formdata["telefon"][i], "SE")
        except:
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i ett giltigt telefonummer för alla målsmän.",'utf-8')
        if not phonenumbers.is_valid_number(phone_number):
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i ett giltigt telefonummer för alla målsmän.",'utf-8')
        if formdata["vuxen_fornamn"][i] == "":
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i förnamn för alla målsmän.",'utf-8')
        if formdata["vuxen_efternamn"][i] == "":
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i efternamn för alla målsmän.",'utf-8')
        if formdata["email"][i] == "":
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Fyll i en email för alla målsmän.",'utf-8')
        data_to_db["adults"].append(
            (
            uuid.uuid4().hex,
            formdata["vuxen_fornamn"][i],
            formdata["vuxen_efternamn"][i],
            formdata["email"][i],
            phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            )
        )

    for adult in data_to_db["adults"]:
        db.cursor.execute("INSERT INTO kontaktpersoner (id,fornamn,efternamn,epost,telefon) VALUES (?,?,?,?,?)",adult)
    
    for kid in data_to_db["kids"]:
        db.cursor.execute("INSERT INTO deltagare (id,kodstugor_id,fornamn,efternamn,kon,klass,skola,datum,status) VALUES (?,?,?,?,?,?,?,?,?)",kid)

    for adult in data_to_db["adults"]:
        for kid in data_to_db["kids"]:
            db.cursor.execute("INSERT INTO kontaktpersoner_deltagare (kontaktpersoner_id, deltagare_id) VALUES (?,?)",(adult[0], kid[0]))

    hittade = (formdata["hittade"][0],)
    db.cursor.execute("INSERT INTO hittade (hittade) VALUES (?)", hittade)
    db.commit()

    mailmessage = texter.get_one("Intresse anmälan")["text"].replace("%kodstuga%",kodstuga)
    mailsubject = "Tack för din intresseanmälan"
    for email in formdata["email"]:
        spawn(send_email, email, mailsubject, mailmessage)
    
    response('200 OK', [('Content-Type', 'text/html')])
    return json.dumps({"applied":data_to_db})
