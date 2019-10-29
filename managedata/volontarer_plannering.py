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
                post_data["status"][i],
                post_data["id"][i]
            )
            db.cursor.execute("""
                UPDATE volontarer_plannering
                    SET
                        status = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                post_data["volontarer_id"][i],
                post_data["datum"][i],
                post_data["status"][i],
            )
            db.cursor.execute("""
                INSERT 
                    INTO volontarer_plannering 
                        (volontarer_id, datum, status) 
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
            volontarer_id,
            datum,
            status
        FROM volontarer_plannering;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    by_volontarer_id = {}

    for date in map(to_headers, all.fetchall()):
        if date['volontarer_id'] not in by_volontarer_id:
            by_volontarer_id[date['volontarer_id']] = {}
        by_volontarer_id[date['volontarer_id']][date['datum']] = {"status":date["status"],"id":date["id"]}

    return json.dumps({"volontarer_plannering":by_volontarer_id})