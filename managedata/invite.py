#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db, deltagare, texter, kontaktpersoner
from tools import send_email, read_post_data, read_get_data, static_file, Error400
import json
import time
from gevent import sleep

def new(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        if "invite" not in post_data:
            raise Error400("Inga deltagare valda.")
        invites = post_data["invite"]
        for invite in invites:
            db.cursor.execute('''
                UPDATE
                    deltagare
                SET 
                    status = "inbjudan"
                WHERE
                    id = ?;
                ''',(invite,))
        db.commit()
    return deltagare.all(request)

def reply(request):
    if request['REQUEST_METHOD'] == 'GET':
        return static_file('static/reply.html')
    invitedata = read_post_data(request)
    deltagar_id = invitedata["id"][0]
    status = invitedata["status"][0]
    if status == "ja":
        foto = invitedata["foto"][0]
    else:
        foto = ""
    db.cursor.execute('''
            UPDATE
                deltagare
            SET 
                status = ?,
                foto = ?
            WHERE
                id = ? 
            AND
                status = "inbjuden";
            ''',(status, foto, deltagar_id))
    db.commit()
    if status == "ja":
        kontakter = kontaktpersoner.fordeltagare(deltagar_id)
        kodstuga = deltagare.get_kodstuga(deltagar_id)
        this_deltagare = deltagare.get_one(deltagar_id)
        meddelande = kodstuga["epost_text_ja"]
        meddelande = meddelande.replace(
                "%namn%",this_deltagare["fornamn"]).replace(
                "%kodstuga%",kodstuga["namn"])
        for kontakt in kontakter:
            send_email(kontakt["epost"], kodstuga["epost_rubrik_ja"], meddelande)
    return static_file('static/reply_done.html')

def send_invites():
    while True:
        sleep(2)
        found = db.cursor.execute('''
            SELECT
                kodstugor.namn AS kodstuga,
                kodstugor.typ AS kodstuga_typ,
                deltagare.id AS deltagare_id,
                deltagare.status AS deltagare_status,
                deltagare.fornamn AS deltagare_fornamn,
                kontaktpersoner.epost AS kontaktperson_epost
            FROM
                deltagare
            INNER JOIN kontaktpersoner_deltagare 
                ON deltagare.id=kontaktpersoner_deltagare.deltagare_id 
            INNER JOIN kontaktpersoner
               ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
            INNER JOIN kodstugor
               ON deltagare.kodstugor_id=kodstugor.id
            WHERE deltagare.status = "inbjudan"
            ORDER BY deltagare.id;
            ''')
        def to_headers(row):
            ut = {}
            for idx, col in enumerate(found.description):
                ut[col[0]] = row[idx]
            return ut
        deltagare_id = False
        for row in list(map(to_headers,found.fetchall())):
            if not deltagare_id:
                deltagare_id = row["deltagare_id"]
            if row["deltagare_id"] != deltagare_id:
                break
            message = texter.get_one("Erbjudande om plats " + row["kodstuga_typ"])["text"]
            link = "https://besk.kodcentrum.se/reply?id="+row["deltagare_id"]
            message = message.replace(
                "%namn%",row["deltagare_fornamn"]).replace(
                "%kodstuga%",row["kodstuga"]).replace(
                "%länk%",link)
            send_email(row["kontaktperson_epost"], "Erbjudande om plats", message)
        db.cursor.execute('''
                UPDATE
                    deltagare
                SET
                    status = "inbjuden"
                WHERE
                    id = ?;
        ''',(deltagare_id,))
        db.commit()




