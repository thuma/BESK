#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import uuid
import json
import phonenumbers

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return all(request)

def add_or_uppdate(request):
    post_data = read_post_data(request)

    try:
        phone_number = phonenumbers.parse(post_data["telefon"][0], "SE")
    except:
        response('400 Bad Request', [('Content-Type', 'text/html')])
        return bytes("Fyll i ett giltigt telefonummer.",'utf-8')
    if not phonenumbers.is_valid_number(phone_number):
        response('400 Bad Request', [('Content-Type', 'text/html')])
        return bytes("Fyll i ett giltigt telefonummer.",'utf-8')

    if "id" in post_data:
        data = (
            post_data["fornamn"][0],
            post_data["efternamn"][0],
            post_data["epost"][0],
            phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164),
            post_data["id"][0]
        )
        db.cursor.execute("""
            UPDATE kontaktpersoner
                SET
                    fornamn = ?,
                    efternamn = ?,
                    epost = ?,
                    telefon = ?
                WHERE
                    id = ?
            """, data)
    else:
        data = (
            uuid.uuid4().hex,
            post_data["fornamn"][0],
            post_data["efternamn"][0],
            post_data["epost"][0],
            phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164),
            post_data["id"][0]
        )
        db.cursor.execute("""
            INSERT 
                INTO kontaktpersoner
                    (id, fornamn, efternamn, epost, telefon) 
                VALUES 
                    (?,?,?,?,?)
            """, data)
    db.commit()
    return all(request)

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = "WHERE deltagare.status = 'ja' AND kodstugor.id = " + str(request["BESK_kodstuga"])
    all = db.cursor.execute("""
        SELECT 
            kontaktpersoner.id AS id,
            kontaktpersoner.fornamn AS fornamn,
            kontaktpersoner.efternamn AS efternamn,
            kontaktpersoner.epost AS epost,
            kontaktpersoner.telefon AS telefon,
            kodstugor.id AS kodstugor_id,
            GROUP_CONCAT(deltagare.id,",") AS deltagare_id
        FROM deltagare
        INNER JOIN kontaktpersoner_deltagare 
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id 
        INNER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        INNER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id
        """ + where + """
        GROUP BY kontaktpersoner.id
        ORDER BY kodstugor.id, deltagare.datum;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "deltagare_id":
                ut[col[0]] = ut[col[0]].split(',')
        return ut
    return {"kontaktpersoner":list(map(to_headers, all.fetchall()))}
