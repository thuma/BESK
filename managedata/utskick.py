#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import json

def all():
    all = db.cursor.execute("""
        SELECT 
            id,
            kodstugor_id,
            typ,
            rubrik,
            text,
            datum,
            status
        FROM utskick ORDER BY kodstugor_id;
     """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return json.dumps({"utskick":list(map(to_headers, all.fetchall()))})
    
def add_or_uppdate(request, response):
    post_data = read_post_data(request)
    if "id" in post_data:
        data = (
            post_data["kodstugor_id"][0],
            post_data["typ"][0],
            post_data["rubrik"][0],
            post_data["text"][0],
            post_data["datum"][0],
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
            post_data["datum"][0],
        )
        db.cursor.execute("""
            INSERT 
                INTO utskick
                    (kodstugor_id, typ, rubrik, text, datum, status) 
                VALUES 
                    (?,?,?,?,?,"väntar")
            """, data)
    db.commit()
    response('200 OK', [('Content-Type', 'text/html')])
    return all()