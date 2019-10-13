#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
import json
from tools import read_post_data

def all():
    all = db.cursor.execute("""
        SELECT 
            kodstugor_id,
            datum,
            typ
        FROM kodstugor_datum;
     """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    datum_id = {}
    for one_datum in list(map(to_headers, all.fetchall())):
        if not one_datum["kodstugor_id"] in datum_id:
            datum_id[one_datum["kodstugor_id"]] = [one_datum]
        else:
            datum_id[one_datum["kodstugor_id"]].append(one_datum)

    return json.dumps({"kodstugor_datum":datum_id})
    
def set(request, response):
    post_data = read_post_data(request)
    if "datum" in post_data:
        data = []
        for i, datum in enumerate(post_data["datum"]):
            data.append((
                post_data["kodstugor_id"][0],
                post_data["datum"][i],
                post_data["typ"][i])
            )
        db.cursor.execute("""
                DELETE FROM
                    kodstugor_datum 
                WHERE kodstugor_id = ?
                """, (data[0][0],))
        for query in data:
            db.cursor.execute("""
                INSERT INTO 
                	kodstugor_datum(kodstugor_id,datum,typ)
				VALUES
					(?, ?, ?);
                """, query)
    db.commit()
    response('200 OK', [('Content-Type', 'text/html')])
    return all()