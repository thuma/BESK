#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import json
import phonenumbers

def all():
    all = db.cursor.execute("""
        SELECT 
            id,
            kodstugor_id,
            epost,
            namn,
            telefon,
            utdrag_datum
        FROM volontarer ORDER BY kodstugor_id;
     """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return json.dumps({"volontärer":list(map(to_headers, all.fetchall()))})
    
def add_or_uppdate(request, response):
    post_data = read_post_data(request)
    try:
        phone_number = phonenumbers.parse(post_data["telefon"][0], "SE")
        phone_number_str = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
    except:
        response('400 Bad Request', [('Content-Type', 'text/html')])
        return bytes("Fyll i ett giltigt telefonummer.",'utf-8')
    if not phonenumbers.is_valid_number(phone_number):
        response('400 Bad Request', [('Content-Type', 'text/html')])
        return bytes("Fyll i ett giltigt telefonummer.",'utf-8')
    if "id" in post_data:
        data = (
            post_data["namn"][0],
            post_data["epost"][0],
            phone_number_str,
            post_data["kodstugor_id"][0],
            post_data["utdrag_datum"][0],
            post_data["id"][0]
        )
        db.cursor.execute("""
            UPDATE volontarer
                SET
                    namn = ?,
                    epost = ?,
                    telefon = ?,
                    kodstugor_id = ?,
                    utdrag_datum = ?
                WHERE
                    id = ?
            """, data)
    else:
        data = (
            post_data["namn"][0],
            post_data["epost"][0],
            phone_number_str,
            post_data["kodstugor_id"][0],
            post_data["utdrag_datum"][0],
        )
        try:
            db.cursor.execute("""
                INSERT 
                    INTO volontarer
                        (namn, epost, telefon, kodstugor_id, utdrag_datum) 
                    VALUES 
                        (?,?,?,?,?)
                """, data)
        except db.sqlite3.IntegrityError:
            response('400 Bad Request', [('Content-Type', 'text/html')])
            return bytes("E-Postadressen finns redan.",'utf-8')
    db.commit()
    response('200 OK', [('Content-Type', 'text/html')])
    return all()