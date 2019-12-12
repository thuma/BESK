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

def get_kodstuga(id):
    all = db.cursor.execute("""
        SELECT 
            kodstugor.id AS id,
            kodstugor.namn AS namn,
            kodstugor.sms_text AS sms_text,
            kodstugor.epost_rubrik AS epost_rubrik,
            kodstugor.epost_text AS epost_text,
            kodstugor.epost_text_ja AS epost_text_ja,
            kodstugor.epost_rubrik_ja AS epost_rubrik_ja,
            kodstugor.open AS open
        FROM 
            deltagare
        INNER JOIN 
            kodstugor
        ON 
           deltagare.kodstugor_id=kodstugor.id
        WHERE 
            deltagare.id = ?
        GROUP BY 
            deltagare.id
        ORDER BY 
            kodstugor.id, deltagare.datum;
     """, (id,))

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return list(map(to_headers, all.fetchall()))[0]


def get_one(id):
    all = db.cursor.execute("""
        SELECT 
            kodstugor.id AS kodstuga_id,
            deltagare.id AS deltagare_id,
            deltagare.datum AS datum,
            deltagare.status AS status,
            deltagare.fornamn AS fornamn,
            deltagare.efternamn AS efternamn,
            deltagare.kon AS kon,
            deltagare.skola AS skola,
            deltagare.klass AS klass,
            deltagare.foto AS foto,
            GROUP_CONCAT(kontaktpersoner.id,",") AS kontaktperson_id
        FROM deltagare
        INNER JOIN kontaktpersoner_deltagare 
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id 
        INNER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        INNER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id
        WHERE deltagare.id = ?
        GROUP BY deltagare.id
        ORDER BY kodstugor.id, deltagare.datum;
     """, (id,))
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "kontaktperson_id":
                ut[col[0]] = ut[col[0]].split(',')
            if ut[col[0]] == None:
                ut[col[0]] = ""
        return ut
    return list(map(to_headers, all.fetchall()))[0]
    
def add_or_uppdate(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        if "id" in post_data:
            data = (
                post_data["fornamn"][0],
                post_data["efternamn"][0],
                post_data["status"][0],
                post_data["kon"][0],
                post_data["foto"][0],
                post_data["klass"][0],
                post_data["skola"][0],
                post_data["kodstuga"][0],
                post_data["id"][0]
            )
            db.cursor.execute("""
                UPDATE deltagare
                    SET
                        fornamn = ?,
                        efternamn = ?,
                        status = ?,
                        kon = ?,
                        foto = ?,
                        klass = ?,
                        skola = ?,
                        kodstugor_id = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                uuid.uuid4().hex,
                post_data["fornamn"][0],
                post_data["efternamn"][0],
                post_data["status"][0],
                post_data["kon"][0],
                post_data["klass"][0],
                post_data["skola"][0],
                post_data["kodstuga"][0]
            )
            db.cursor.execute("""
                INSERT 
                    INTO deltagare 
                        (id, fornamn, efternamn, status, kon, klass, skola,kodstugor_id) 
                    VALUES 
                        (?,?,?,?,?,?,?)
                """, data)
    else:
        post_data = read_post_data(request)
        data = (
                post_data["fornamn"][0],
                post_data["efternamn"][0],
                post_data["id"][0],
                request["BESK_kodstuga"]
            )
        db.cursor.execute("""
                UPDATE deltagare
                    SET
                        fornamn = ?,
                        efternamn = ?
                    WHERE
                        id = ?
                    AND
                        kodstugor_id = ?
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
            kodstugor.id AS kodstuga_id,
            deltagare.id AS deltagare_id,
            deltagare.datum AS datum,
            deltagare.status AS status,
            deltagare.fornamn AS fornamn,
            deltagare.efternamn AS efternamn,
            deltagare.foto AS foto,
            deltagare.kon AS kon,
            deltagare.skola AS skola,
            deltagare.klass AS klass,
            GROUP_CONCAT(kontaktpersoner.id,",") AS kontaktperson_id
        FROM deltagare
        INNER JOIN kontaktpersoner_deltagare 
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id 
        INNER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        INNER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id
        """ + where + """
        GROUP BY deltagare.id
        ORDER BY kodstugor.id, deltagare.datum;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "kontaktperson_id":
                ut[col[0]] = ut[col[0]].split(',')
            if ut[col[0]] == None:
                ut[col[0]] = ""
        return ut

    return {"deltagare":list(map(to_headers, all.fetchall()))}