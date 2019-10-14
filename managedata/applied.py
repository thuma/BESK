#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import send_email, read_post_data
import uuid
import json
import phonenumbers

def new(request, response):
    data_to_db = {
        "kids":[],
        "adults":[]
        }
    formdata = read_post_data(request)
    kodstugaid = formdata["kodstuga"][0]
    kodstuga = db.cursor.execute("""
        SELECT namn
        FROM kodstugor WHERE id = ?;
     """,(kodstugaid,)).fetchall()[0][0]
   
    for i, value in enumerate(formdata["barn_efternamn"]):
        data_to_db["kids"].append(
            (
            uuid.uuid4().hex,
            kodstugaid,
            formdata["barn_fornamn"][i],
            formdata["barn_efternamn"][i],
            formdata["kon"][i],
            formdata["klass"][i],
            formdata["skola"][i]
            )
        )

    for i, value in enumerate(formdata["vuxen_efternamn"]):

        phone_number= phonenumbers.parse(formdata["telefon"][i], "SE")
        if not phonenumbers.is_valid_number(phone_number):
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("Telefonummret är inte giltigt.",'utf-8')
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
        db.cursor.execute("INSERT INTO deltagare (id,kodstugor_id,fornamn,efternamn,kon,klass,skola) VALUES (?,?,?,?,?,?,?)",kid)

    for adult in data_to_db["adults"]:
        for kid in data_to_db["kids"]:
            db.cursor.execute("INSERT INTO kontaktpersoner_deltagare (kontaktpersoner_id, deltagare_id) VALUES (?,?)",(adult[0], kid[0]))

    hittade = (formdata["hittade"][0],)
    db.cursor.execute("INSERT INTO hittade (hittade) VALUES (?)", hittade)
    db.commit()

    mailmessage = """Hej!

Vi har mottagit din intresseanmälan till Kodstugan på %kodstuga%
och återkommer till dig via mail så snart vi fördelat platserna. Det finns ett
begränsat antal platser vilket innebär att ditt barn inte är garanterad en plats.
Vi strävar efter en jämn fördelning mellan könen samt att samarbetsskolor har
företräde men utgår annars efter en först till kvarn-princip.

Med vänliga hälsningar,
Kodcentrum
info@kodcentrum.se""".replace("%kodstuga%",kodstuga)
    mailsubject = "Tack för din intresseanmälan"
    for email in formdata["email"]:
        send_email(email, mailsubject, mailmessage)
    
    response('200 OK', [('Content-Type', 'text/html')])
    return json.dumps({"applied":data_to_db})

def all():
    all = db.cursor.execute("""
        SELECT 
            kodstugor.namn AS kodstuga,
            kodstugor.id AS kodstuga_id,
            deltagare.id AS deltagare_id,
            deltagare.fornamn AS deltagare_fornamn,
            deltagare.efternamn AS deltagare_efternamn,
            deltagare.kon AS deltagare_kon,
            deltagare.skola AS deltagare_skola,
            deltagare.klass AS deltagare_klass,
            GROUP_CONCAT(kontaktpersoner.id,",") AS kontaktperson_id
        FROM deltagare
        INNER JOIN kontaktpersoner_deltagare 
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id 
        INNER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        INNER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id
        GROUP BY deltagare.id;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "kontaktperson_id":
            	ut[col[0]] = ut[col[0]].split(',')
        return ut

    return json.dumps({"kids":list(map(to_headers, all.fetchall()))})
