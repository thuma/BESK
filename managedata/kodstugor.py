#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import json

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return all(request)

def active():
    all = db.cursor.execute("""
        SELECT 
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text,
            epost_text_ja,
            epost_rubrik_ja,
            open
        FROM kodstugor WHERE open ='Ja';
     """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return {"kodstugor":list(map(to_headers, all.fetchall()))}

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = "WHERE id = " + str(request["BESK_kodstuga"])
    all = db.cursor.execute("""
        SELECT 
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text,
            epost_text_ja,
            epost_rubrik_ja,
            open
        FROM kodstugor
     """ + where);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return {"kodstugor":list(map(to_headers, all.fetchall()))}
    
def add_or_uppdate(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        if "id" in post_data:
            data = (
                post_data["namn"][0],
                post_data["sms_text"][0],
                post_data["epost_text"][0],
                post_data["epost_rubrik"][0],
                post_data["epost_text_ja"][0],
                post_data["epost_rubrik_ja"][0],
                post_data["open"][0],
                post_data["id"][0]
            )
            db.cursor.execute("""
                UPDATE kodstugor
                    SET
                        namn = ?,
                        sms_text = ?,
                        epost_text = ?,
                        epost_rubrik = ?,
                        epost_text_ja = ?,
                        epost_rubrik_ja = ?,
                        open = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                post_data["namn"][0],
                post_data["sms_text"][0],
                post_data["epost_text"][0],
                post_data["epost_rubrik"][0],
                post_data["epost_text_ja"][0],
                post_data["epost_rubrik_ja"][0],
                post_data["open"][0],
            )
            db.cursor.execute("""
                INSERT 
                    INTO kodstugor 
                        (namn, sms_text, epost_text, epost_rubrik, epost_text_ja, epost_rubrik_ja, open) 
                    VALUES 
                        (?,?,?,?,?,?,?)
                """, data)
        db.commit()
    return all(request)
