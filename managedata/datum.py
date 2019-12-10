#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db, kodstugor, kontaktpersoner
import json
from tools import read_post_data, send_email, send_sms
import arrow
import logging
from gevent import sleep
logger = logging.getLogger("datum")

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return set(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return all(request)

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = "WHERE kodstugor_id = " + str(request["BESK_kodstuga"])
    all = db.cursor.execute("""
        SELECT 
            kodstugor_id,
            datum,
            typ
        FROM
            kodstugor_datum
     """ + where);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    datum_id = {}
    for one_datum in list(map(to_headers, all.fetchall())):
        if not one_datum["kodstugor_id"] in datum_id:
            datum_id[one_datum["kodstugor_id"]] = [one_datum]
        else:
            datum_id[one_datum["kodstugor_id"]].append(one_datum)

    return {"kodstugor_datum":datum_id}
    
def set(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        if "datum" in post_data:
            data = []
            for i, datum in enumerate(post_data["datum"]):
                data.append((
                    post_data["kodstugor_id"][0],
                    post_data["datum"][i],
                    post_data["typ"][i])
                )
            db.cursor.execute("""
                    DELETE FROM
                        kodstugor_datum
                    WHERE
                        kodstugor_id = ?;
                    """, (data[0][0],))
            for query in data:
                db.cursor.execute("""
                    INSERT INTO 
                        kodstugor_datum(kodstugor_id,datum,typ)
                    VALUES
                        (?, ?, ?);
                    """, query)
        db.commit()
    return all(request)

def send_sms_reminders():
    while True:
        datum = arrow.utcnow().to('Europe/Stockholm').format('YYYY-MM-DD')
        logger.info("Sending SMS reminders for: " + datum)
        found = db.cursor.execute('''
            SELECT 
                id,
                kodstugor_id,
                datum,
                status
            FROM 
                kodstugor_datum
            WHERE
                datum = ?
            ORDER BY
                datum;
            ''',(datum, ))
        def to_headers(row):
            ut = {}
            for idx, col in enumerate(found.description):
                ut[col[0]] = row[idx]
            return ut
        for utskick in list(map(to_headers, found.fetchall())):
            kodstuga = kodstugor.get_kodstuga(utskick["kodstugor_id"])
            for mottagare in kontaktpersoner.for_kodstuga(utskick["kodstugor_id"]):
                link = "https://besk.kodcentrum.se/svar?id=" + mottagare["deltagare_id"] + "&datum=" + datum
                message = kodstuga["sms_text"].replace(
                    "%namn%", mottagare["deltagare_fornamn"]).replace(
                    "%kodstuga%", mottagare["kodstugor_namn"]).replace(
                    "%datum%", datum).replace(
                    "%länk%", link)
                if len(kodstuga["sms_text"]) > 4:
                    send_sms(mottagare["telefon"], message)
        now = arrow.utcnow().timestamp
        then = arrow.utcnow().shift(hours=24).replace(hour=9, minute=00).timestamp
        sleep(then - now)

def send_email_reminders():
    while True:
        datum = arrow.utcnow().shift(hours=24).to('Europe/Stockholm').format('YYYY-MM-DD')
        logger.info("Sending Email reminders for: " + datum)
        found = db.cursor.execute('''
            SELECT 
                id,
                kodstugor_id,
                datum,
                status
            FROM 
                kodstugor_datum
            WHERE
                datum = ?
            ORDER BY
                datum;
            ''',(datum, ))
        def to_headers(row):
            ut = {}
            for idx, col in enumerate(found.description):
                ut[col[0]] = row[idx]
            return ut
        for utskick in list(map(to_headers, found.fetchall())):
            kodstuga = kodstugor.get_kodstuga(utskick["kodstugor_id"])
            for mottagare in kontaktpersoner.for_kodstuga(utskick["kodstugor_id"]):
                link = "https://besk.kodcentrum.se/svar?id="+mottagare["deltagare_id"]+"&datum=" + datum
                message = kodstuga["epost_text"].replace(
                    "%namn%", mottagare["deltagare_fornamn"]).replace(
                    "%kodstuga%", mottagare["kodstugor_namn"]).replace(
                    "%datum%", datum).replace(
                    "%länk%", link)
                send_email(mottagare["epost"], kodstuga["epost_rubrik"], message)
        now = arrow.utcnow().timestamp
        then = arrow.utcnow().shift(hours=24).replace(hour=9, minute=00).timestamp
        sleep(then - now)
