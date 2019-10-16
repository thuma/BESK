#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db, applied
from tools import send_email, read_post_data, read_get_data
import json
import time
from gevent import sleep

def new(request, response):
    post_data = read_post_data(request)
    invites = post_data["invite"]
    for invite in invites:
        db.cursor.execute('''
            UPDATE deltagare
            SET status = "inbjudan"
            WHERE
            id = ?
            ''',(invite,))
    db.commit()
    response('200 OK', [('Content-Type', 'text/html')])
    return applied.all()

def reply(request, response):
    invitedata = read_get_data(request)
    delragar_id = invitedata["id"][0]
    status = invitedata["status"][0]
    db.cursor.execute('''
            UPDATE deltagare
            SET status = ?
            WHERE
            id = ? 
            AND
            status = "inbjuden";
            ''',(status, delragar_id))
    db.commit()
    response('200 OK', [('Content-Type', 'text/html')])
    return "Tack nu är anmälan bekräftad."

def send_invites():
    while True:
        sleep(2)
        found = db.cursor.execute('''
            SELECT 
                kodstugor.namn AS kodstuga,
                deltagare.id AS deltagare_id,
                deltagare.status AS deltagare_status,
                deltagare.fornamn AS deltagare_fornamn,
                kontaktpersoner.epost AS kontaktperson_epost
            FROM deltagare 
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
            message = '''Hej!
%namn% har fått plats på kodstgan %kodstuga% du behöver bekräfta platsen.

Om du vill bekräfta platsen tryck på denna länk: %jalänk%

Om du inte vill ha platsen så tryck på denna länk: %nejlänk%

Med vänliga hälsningar,
Kodcentrum
info@kodcentsrum.se'''
            link = "https://besk.kodcentrum.se/reply?status="
            message = message.replace(
                "%namn%",row["deltagare_fornamn"]).replace(
                "%kodstuga%",row["kodstuga"]).replace(
                "%jalänk%",link+"ja&id="+row["deltagare_id"]).replace(
                "%nejlänk%",link+"nej&id="+row["deltagare_id"])
            send_email(row["kontaktperson_epost"],"Inbjudan", message)
        db.cursor.execute('''
                UPDATE deltagare
                SET status = "inbjuden"
                WHERE
                id = ?;
        ''',(deltagare_id,))
        db.commit()

