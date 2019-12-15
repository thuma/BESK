#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db, login, kontaktpersoner
from tools import read_post_data
import json

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return delete(request)

def delete(request):
    post_data = read_post_data(request)
    if request["BESK_admin"] and len(kontaktpersoner.for_kodstuga(post_data['id'][0])) == 0:
        db.cursor.execute("""
            DELETE FROM 
                kodstugor
            WHERE 
                id = ?
         """,(post_data['id'][0],))
    return all(request)

def active(request):
    if request["BESK_login"]["user"] and login.is_admin(request["BESK_login"]["user"]["user"]["email"]):
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
            FROM kodstugor;
         """);
        admin = True;
    else:
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
        admin = False;

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return {"admin":admin, "kodstugor":list(map(to_headers, all.fetchall()))}

def get_kodstuga(kodstua_id):
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
        FROM
            kodstugor
        WHERE
            id = ?
     """, (kodstua_id,));
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return list(map(to_headers, all.fetchall()))[0]

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
