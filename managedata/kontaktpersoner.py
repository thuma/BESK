#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
import json

def all():
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
        GROUP BY kontaktpersoner.id
        ORDER BY kodstugor.id, deltagare.datum;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "deltagare_id":
                ut[col[0]] = ut[col[0]].split(',')
        return ut
    return json.dumps({"kontaktpersoner":list(map(to_headers, all.fetchall()))})
