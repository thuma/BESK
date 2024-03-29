#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import time

import phonenumbers

from managedata import db, texter, login
from tools import send_email, read_post_data, Error400


def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return {}
    if request['REQUEST_METHOD'] == 'POST':
        return new(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return {}
    return {}


def new(request):
    data_to_db = {
        "kids": [],
        "adults": []
    }
    status = "ansökt"
    formdata = read_post_data(request)
    if request["BESK_login"]["user"]:
        user_is_admin = login.is_admin(request["BESK_login"]["user"]["user"]["email"])
    else:
        user_is_admin = False
    if "invite_now" in formdata:
        if user_is_admin and formdata["invite_now"][0] == "inbjudan":
            status = "inbjudan"
        if user_is_admin and formdata["invite_now"][0] == "ja":
            status = "ja"

    if "approve" not in formdata:
        raise Error400("Du måste acceptera Kodcentrums Integritetspolicy.")
    try:
        kodstugaid = formdata["kodstuga"][0]
        (kodstuga, kodstuga_typ) = db.cursor.execute("""
            SELECT namn, typ
            FROM kodstugor WHERE id = ?;
        """, (kodstugaid,)).fetchone()
    except Exception:
        raise Error400("Välj en aktivitet.")
    now = int(time.time())

    for i, _ in enumerate(formdata["barn_efternamn"]):
        if user_is_admin:
            foto = formdata["foto"][i]
        else:
            foto = None
        if formdata["barn_fornamn"][i] == "":
            raise Error400("Fyll i förnamn för samtliga barn.")
        if formdata["barn_efternamn"][i] == "":
            raise Error400("Fyll i efternamn för samtliga barn.")
        if formdata["kon"][i] == "":
            raise Error400("Fyll i kön för samtliga barn.")
        if formdata["klass"][i] == "":
            raise Error400("Fyll i klass för samtliga barn.")
        if formdata["skola"][i] == "":
            raise Error400("Fyll i skola för samtliga barn.")
        data_to_db["kids"].append(
            (
                uuid.uuid4().hex,
                kodstugaid,
                formdata["barn_fornamn"][i],
                formdata["barn_efternamn"][i],
                formdata["kon"][i],
                formdata["klass"][i],
                formdata["skola"][i],
                foto,
                now,
                status
            )
        )

    for i, value in enumerate(formdata["vuxen_efternamn"]):
        try:
            phone_number = phonenumbers.parse(formdata["telefon"][i], "SE")
        except Exception:
            raise Error400("Fyll i ett giltigt telefonummer för alla målsmän.")
        if not phonenumbers.is_valid_number(phone_number):
            raise Error400("Fyll i ett giltigt telefonummer för alla målsmän.")
        if formdata["vuxen_fornamn"][i] == "":
            raise Error400("Fyll i förnamn för alla målsmän.")
        if formdata["vuxen_efternamn"][i] == "":
            raise Error400("Fyll i efternamn för alla målsmän.")
        if formdata["email"][i] == "":
            raise Error400("Fyll i en email för alla målsmän.")
        data_to_db["adults"].append(
            (
                uuid.uuid4().hex,
                formdata["vuxen_fornamn"][i],
                formdata["vuxen_efternamn"][i],
                formdata["email"][i],
                phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            )
        )

    for kid in data_to_db["kids"]:
        db.cursor.execute("INSERT INTO deltagare (id,kodstugor_id,fornamn,efternamn,kon,klass,skola,foto,datum,status) VALUES (?,?,?,?,?,?,?,?,?,?)", kid)  # noqa: E501

    for adult in data_to_db["adults"]:
        db.cursor.execute("INSERT INTO kontaktpersoner (id,fornamn,efternamn,epost,telefon) VALUES (?,?,?,?,?)", adult)

    for adult in data_to_db["adults"]:
        for kid in data_to_db["kids"]:
            db.cursor.execute(
                "INSERT INTO kontaktpersoner_deltagare (kontaktpersoner_id, deltagare_id) VALUES (?,?)",
                (adult[0], kid[0])
            )

    hittade = (formdata["hittade"][0],)
    db.cursor.execute("INSERT INTO hittade (hittade) VALUES (?)", hittade)
    db.commit()
    if status == "ansökt":
        mailmessage = texter.get_one("Intresseanmälan " + kodstuga_typ)["text"].replace("%kodstuga%", kodstuga)
        mailsubject = "Tack för din intresseanmälan"
        for email in formdata["email"]:
            send_email(email, mailsubject, mailmessage)

    return {"applied": data_to_db}
