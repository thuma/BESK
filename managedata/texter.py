#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import json

def add_or_uppdate(request, response):
    post_data = read_post_data(request)
    for i in range(len(post_data["id"])):
        if not post_data["id"][i] == "0":
            data = (
                post_data["text"][i],
                post_data["id"][i]
            )
            db.cursor.execute("""
                UPDATE keyvalue
                    SET
                        text = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                post_data["id"][i],
                post_data["text"][i]

            )
            db.cursor.execute("""
                INSERT 
                    INTO keyvalue 
                        (id, text) 
                    VALUES 
                        (?,?)
                """, data)
    db.commit()
    response('200 OK', [('Content-Type', 'text/html')])
    return all()

def get_one(id):
    one = db.cursor.execute("""
        SELECT 
            id,
            text
        FROM keyvalue WHERE id = ? LIMIT 1;
     """, (id,))
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return list(map(to_headers, all.fetchall()))[0]

def all():
    all = db.cursor.execute("""
        SELECT 
            id,
            text
        FROM keyvalue;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return json.dumps({"texter":list(map(to_headers, all.fetchall()))})