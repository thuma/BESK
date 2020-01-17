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
        return delete(request)

def add_or_uppdate(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        for i in range(len(post_data["id"])):
            if "new" not in post_data:
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
                    INSERT INTO
                        keyvalue (id,text)
                    VALUES 
                        (?,?)
                    """, data)
        db.commit()
    return all(request)

def delete(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        db.cursor.execute("""
            DELETE FROM 
                keyvalue
            WHERE 
                id = ?
         """,(post_data['id'][0],))
    return all(request)

def get_one(id):
    one = db.cursor.execute("""
        SELECT 
            id,
            text
        FROM
            keyvalue
        WHERE
            id = ?
        LIMIT 1;
     """, (id,))
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(one.description):
            ut[col[0]] = row[idx]
        return ut
    return to_headers(one.fetchone())

def all(request):
    all = db.cursor.execute("""
        SELECT 
            id,
            text
        FROM
            keyvalue;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return {"texter":list(map(to_headers, all.fetchall()))}