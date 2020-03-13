#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data, Error400
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
         raise Error400("Fyll i ett giltigt telefonummer.")
    if not phonenumbers.is_valid_number(phone_number):
         raise Error400("Fyll i ett giltigt telefonummer.")

    if request["BESK_admin"]:
        if "deltagare_id" not in post_data:
            post_data["deltagare_id"] = []
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
            db.cursor.execute("""
                DELETE FROM 
                    kontaktpersoner_deltagare
                WHERE 
                    kontaktpersoner_id = ?
                """, (post_data["id"][0], ))
            for deltagare_id in post_data["deltagare_id"]:
                db.cursor.execute("""
                INSERT 
                    INTO kontaktpersoner_deltagare
                        (deltagare_id, kontaktpersoner_id) 
                    VALUES 
                        (?,?)
                """, (deltagare_id, post_data["id"][0]))
        else:
            data = (
                uuid.uuid4().hex,
                post_data["fornamn"][0],
                post_data["efternamn"][0],
                post_data["epost"][0],
                phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            )
            db.cursor.execute("""
                INSERT 
                    INTO kontaktpersoner
                        (id, fornamn, efternamn, epost, telefon) 
                    VALUES 
                        (?,?,?,?,?)
                """, data)
            for deltagare_id in post_data["deltagare_id"]:
                db.cursor.execute("""
                INSERT 
                    INTO kontaktpersoner_deltagare
                        (deltagare_id, kontaktpersoner_id) 
                    VALUES 
                        (?,?)
                """, (deltagare_id, data[0]))
        db.commit()
    return all(request)

def for_kodstuga(kodstugor_id):
    all = db.cursor.execute("""
        SELECT 
            kontaktpersoner.id AS id,
            kontaktpersoner.fornamn AS fornamn,
            kontaktpersoner.efternamn AS efternamn,
            kontaktpersoner.epost AS epost,
            kontaktpersoner.telefon AS telefon,
            kodstugor.namn AS kodstugor_namn,
            deltagare.fornamn AS deltagare_fornamn,
            deltagare.efternamn AS deltagare_efternamn,
            deltagare.id AS deltagare_id
        FROM 
            deltagare
        INNER JOIN 
            kontaktpersoner_deltagare 
        ON 
            deltagare.id=kontaktpersoner_deltagare.deltagare_id 
        INNER JOIN 
            kontaktpersoner
        ON 
            kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        INNER JOIN
            kodstugor
        ON 
            deltagare.kodstugor_id=kodstugor.id
        WHERE
            kodstugor.id = ?
        AND 
            deltagare.status = "ja"
        GROUP BY
            deltagare.id
     """, (kodstugor_id,))
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return list(map(to_headers, all.fetchall()))

def fordeltagare(deltagar_id):
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
        WHERE deltagare.id = ?
        GROUP BY kontaktpersoner.id
        ORDER BY kodstugor.id, deltagare.datum;
     """, (deltagar_id,))
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "deltagare_id":
                ut[col[0]] = ut[col[0]].split(',')
        return ut
    return list(map(to_headers, all.fetchall()))

def all(request):
    if request["BESK_admin"]:
        sql_query = """
        SELECT 
            kontaktpersoner.id AS id,
            kontaktpersoner.fornamn AS fornamn,
            kontaktpersoner.efternamn AS efternamn,
            kontaktpersoner.epost AS epost,
            kontaktpersoner.telefon AS telefon,
            kodstugor.id AS kodstugor_id,
            GROUP_CONCAT(deltagare.id,",") AS deltagare_id
        FROM kontaktpersoner
        LEFT OUTER JOIN kontaktpersoner_deltagare
            ON kontaktpersoner_deltagare.kontaktpersoner_id = kontaktpersoner.id
        LEFT OUTER JOIN deltagare
           ON deltagare.id = kontaktpersoner_deltagare.deltagare_id
        LEFT OUTER JOIN kodstugor
           ON deltagare.kodstugor_id = kodstugor.id
        GROUP BY kontaktpersoner.id
        ORDER BY kodstugor.id, deltagare.datum;
        """
    else:
        sql_query = """
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
        WHERE 
                deltagare.status = 'ja' 
            AND 
                kodstugor.id
            IN (
                SELECT 
                    kodstugor_id 
                FROM 
                    volontarer_roller
                WHERE 
                    volontarer_id = %s
            )
        GROUP BY kontaktpersoner.id
        ORDER BY kodstugor.id, deltagare.datum;
     """ % request["BESK_volontarer_id"]
    all = db.cursor.execute(sql_query)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "deltagare_id":
                if row[idx] == None:
                    ut[col[0]] = []
                else:
                    ut[col[0]] = ut[col[0]].split(',')
        return ut
    return {"kontaktpersoner":list(map(to_headers, all.fetchall()))}
