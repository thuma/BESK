#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
import json

def all():
    all = db.cursor.execute("""
        SELECT 
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text
        FROM kodstugor;
     """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return bytes(json.dumps({"kodstugor":list(map(to_headers, all.fetchall()))}),'utf-8')
    
def add_or_uppdate(request, response):
    post_data = read_post_data(request)
    if post_data["id"]:
        data = (
            post_data["namn"],
            post_data["sms_text"],
            post_data["epost_text"],
            post_data["epost_rubrik"],
            post_data["id"]
        )
        db.cursor.execute("""
            UPDATE kodstugor
                SET
                    namn = ?,
                    sms_text = ?,
                    epost_text = ?,
                    epost_rubrik = ?
                WHERE
                    id = ?
            """, data)
        db.commit()
    else:
        data = (
            post_data["namn"],
            post_data["sms_text"],
            post_data["epost_text"],
            post_data["epost_rubrik"],
        )
        db.cursor.execute("""
            INSERT 
                INTO kodstugor 
                    (namn, sms_text, epost_text, epost_rubrik) 
                VALUES 
                    (?,?,?,?)
            """, data)
        db.commit()
    if request.query.get('id'):
        id = int(request.query.get('id'))
    else:
        id = 0
    all = db.cursor.execute("""
        SELECT 
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text
        FROM kodstugor;
     """)
    response('200 OK', [('Content-Type', 'text/html')])
    return json.dumps({"kodstugor":list(map(to_headers, all.fetchall()))})
