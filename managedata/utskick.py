#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db, kontaktpersoner
from tools import read_post_data, send_email, send_sms
from gevent import sleep
import time
import json
import arrow
import logging
logger = logging.getLogger("utskick")

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return delete(request)

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = "WHERE kodstugor_id = " + str(request["BESK_kodstuga"])
    all = db.cursor.execute("""
        SELECT 
            id,
            kodstugor_id,
            typ,
            rubrik,
            text,
            datum,
            status
        FROM
            utskick 
        """ + 
        where + 
        """
        ORDER BY
            kodstugor_id;
        """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "datum":
                ut[col[0]] = arrow.Arrow.utcfromtimestamp(row[idx]).format("YYYY-MM-DD")
        return ut
    return {"utskick":list(map(to_headers, all.fetchall()))}

def delete(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        db.cursor.execute("""
            DELETE FROM 
                utskick
            WHERE 
                id = ?
         """,(post_data['id'][0],))
    return all(request)

def add_or_uppdate(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        if "id" in post_data:
            data = (
                post_data["kodstugor_id"][0],
                post_data["typ"][0],
                post_data["rubrik"][0],
                post_data["text"][0],
                arrow.get(post_data["datum"][0]).timestamp,
                post_data["id"][0]
            )
            db.cursor.execute("""
                UPDATE utskick
                    SET
                        kodstugor_id = ?,
                        typ = ?,
                        rubrik = ?,
                        text = ?,
                        datum = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                post_data["kodstugor_id"][0],
                post_data["typ"][0],
                post_data["rubrik"][0],
                post_data["text"][0],
                arrow.get(post_data["datum"][0]).timestamp,
            )
            db.cursor.execute("""
                INSERT 
                    INTO utskick
                        (kodstugor_id, typ, rubrik, text, datum, status) 
                    VALUES 
                        (?,?,?,?,?,"väntar")
                """, data)
        db.commit()
    return all(request)

def send_utskick():
    while True:
        found = db.cursor.execute('''
            SELECT 
                id,
                kodstugor_id,
                typ,
                rubrik,
                text,
                datum,
                status
            FROM 
                utskick 
            WHERE
                datum < ?
            AND
                status = "väntar"
            ORDER BY
                datum;
            ''',(int(time.time()),))
        def to_headers(row):
            ut = {}
            for idx, col in enumerate(found.description):
                ut[col[0]] = row[idx]
            return ut
        for utskick in list(map(to_headers,found.fetchall())):
            for mottagare in kontaktpersoner.for_kodstuga(utskick["kodstugor_id"]):
                message = utskick["text"].replace(
                    "%namn%", mottagare["deltagare_fornamn"]).replace(
                    "%kodstuga%", mottagare["kodstugor_namn"])
                if utskick["typ"] == "sms":
                    send_sms(mottagare["telefon"], message)
                elif utskick["typ"] == "e-post":
                    send_email(mottagare["epost"], utskick["rubrik"], message)
            db.cursor.execute('''
                    UPDATE 
                        utskick
                    SET 
                        status = "skickad"
                    WHERE
                        id = ?;
            ''',(utskick["id"],))
            db.commit()
        now = arrow.utcnow().timestamp
        then = arrow.utcnow().shift(hours=24).replace(hour=9, minute=30).timestamp
        sleep(then - now)