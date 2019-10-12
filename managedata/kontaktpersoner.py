#!/usr/bin/env python
# -*- coding: utf-8 -*-

from managedata import db
import json

def all():
    all = db.cursor.execute("""
        SELECT 
        	id,
        	fornamn,
 			efternamn,
  			epost,
  			telefon
        FROM
        	kontaktpersoner;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return json.dumps({"kontaktpersoner":list(map(to_headers, all.fetchall()))})
