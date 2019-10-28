#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import uuid
import json
import phonenumbers

def add_or_uppdate(request, response):
    post_data = read_post_data(request)
    if "id" in post_data:
        data = (
            post_data["fornamn"][0],
            post_data["efternamn"][0],
            post_data["status"][0],
            post_data["kon"][0],
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
    db.commit()
    response('200 OK', [('Content-Type', 'text/html')])
    return all()

def all():
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
            GROUP_CONCAT(kontaktpersoner.id,",") AS kontaktperson_id
        FROM deltagare
        INNER JOIN kontaktpersoner_deltagare 
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id 
        INNER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        INNER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id
        GROUP BY deltagare.id
        ORDER BY kodstugor.id, deltagare.datum;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "kontaktperson_id":
            	ut[col[0]] = ut[col[0]].split(',')
        return ut

    return json.dumps({"deltagare":list(map(to_headers, all.fetchall()))})