#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data
import json

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all()
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return all()

def add_or_uppdate(request):
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
        for idx, col in enumerate(one.description):
            ut[col[0]] = row[idx]
        return ut
    return list(map(to_headers, one.fetchall()))[0]

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
    return {"texter":list(map(to_headers, all.fetchall()))}