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
                post_data["kodstugor_id"][i],
                post_data["datum"][i],
                post_data["status"][i],
                post_data["kommentar"][i],
            )
            db.cursor.execute("""
                INSERT 
                    INTO volontarer_plannering (
                        volontarer_id,
                        kodstugor_id,
                        datum,
                        status,
                        kommentar
                        ) 
                    VALUES 
                        (?,?,?,?,?)
                """, data)
    db.commit()
    return all(request)

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = """
            WHERE 
                volontarer_plannering.kodstugor_id
            IN (
                SELECT 
                    kodstugor_id 
                FROM 
                    volontarer_roller
                WHERE 
                    volontarer_id = %s
            );""" % request["BESK_volontarer_id"]
    all = db.cursor.execute("""
        SELECT 
            volontarer_plannering.id as id,
            volontarer_plannering.volontarer_id as volontarer_id,
            volontarer_plannering.kodstugor_id as kodstugor_id,
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

    return {"volontarer_plannering":list(map(to_headers, all.fetchall())), "volontarer_redigerade":{}}