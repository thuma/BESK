#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import json

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return all(request)

def add_or_uppdate(request):
    post_data = read_post_data(request)
    for i in range(len(post_data["id"])):
        if not post_data["id"][i] == "0":
            data = (
                post_data["status"][i],
                post_data["kommentar"][i],
                post_data["id"][i],
            )
            db.cursor.execute("""
                UPDATE volontarer_plannering
                    SET
                        status = ?,
                        kommentar = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                post_data["volontarer_id"][i],
                post_data["datum"][i],
                post_data["status"][i],
                post_data["kommentar"][i],
            )
            db.cursor.execute("""
                INSERT 
                    INTO volontarer_plannering 
                        (volontarer_id, datum, status, kommentar) 
                    VALUES 
                        (?,?,?,?)
                """, data)
    db.commit()
    return all(request)

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = """
            INNER JOIN 
                volontarer 
            ON
                volontarer.id = volontarer_plannering.volontarer_id
            WHERE
                volontarer.kodstugor_id = """ + str(request["BESK_kodstuga"])
    all = db.cursor.execute("""
        SELECT 
            volontarer_plannering.id as id,
            volontarer_plannering.volontarer_id as volontarer_id,
            volontarer_plannering.datum as datum,
            volontarer_plannering.status as status,
            volontarer_plannering.kommentar as kommentar
        FROM volontarer_plannering
     """ + where)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    by_volontarer_id = {}

    for date in map(to_headers, all.fetchall()):
        if date['volontarer_id'] not in by_volontarer_id:
            by_volontarer_id[date['volontarer_id']] = {}
        by_volontarer_id[date['volontarer_id']][date['datum']] = {"kommentar":date["kommentar"],"status":date["status"],"id":date["id"]}

    return {"volontarer_plannering":by_volontarer_id,"volontarer_redigerade":{}}