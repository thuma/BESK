#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import json
from time import time

def add_or_uppdate(request, response):
    post_data = read_post_data(request)
    for i in range(len(post_data["id"])):
        if not post_data["id"][i] == "0":
            data = (
                post_data["status"][i],
                post_data["id"][i]
            )
            db.cursor.execute("""
                UPDATE deltagande_närvaro
                    SET
                        status = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                post_data["deltagare_id"][i],
                post_data["datum"][i],
                post_data["status"][i],
                int(time())

            )
            db.cursor.execute("""
                INSERT 
                    INTO deltagande_närvaro 
                        (deltagare_id, datum, status, skapad) 
                    VALUES 
                        (?,?,?)
                """, data)
    db.commit()
    response('200 OK', [('Content-Type', 'text/html')])
    return all()

def all():
    all = db.cursor.execute("""
        SELECT 
            id,
            deltagare_id,
            datum,
            status,
            skapad
        FROM deltagande_närvaro;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    by_volontarer_id = {}

    for date in map(to_headers, all.fetchall()):
        if date['deltagare_id'] not in by_volontarer_id:
            by_volontarer_id[date['deltagare_id']] = {}
        by_volontarer_id[date['deltagare_id']][date['datum']] = {"status":date["status"],"id":date["id"]}

    return json.dumps({"deltagande_närvaro":by_volontarer_id,"närvaro_redigerade":{}})