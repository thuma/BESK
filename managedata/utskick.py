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

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = "WHERE kodstugor_id = " + str(request["BESK_kodstuga"])
    all = db.cursor.execute("""
        SELECT 
            id,
            kodstugor_id,
            typ,
            rubrik,
            text,
            datum,
            status
        FROM utskick 
        """ + 
        where + 
        """
        ORDER BY kodstugor_id;
        """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return {"utskick":list(map(to_headers, all.fetchall()))}
    
def add_or_uppdate(request):
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
    return all(request)