#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from time import time

from managedata import db
from tools import read_post_data, Error400

logger = logging.getLogger("naravro")


def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return all(request)


def add_or_uppdate(request):
    post_data = read_post_data(request)
    if "id" not in post_data:
        raise Error400("Inga ändringar sparade.")
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
                        (?,?,?,?)
                """, data)
    db.commit()
    return all(request)


def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = """
            WHERE
                deltagare.status = 'ja'
            AND
                deltagare.kodstugor_id
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
            deltagande_närvaro.id as id,
            deltagande_närvaro.deltagare_id as deltagare_id,
            deltagande_närvaro.datum as datum,
            deltagande_närvaro.status as status,
            deltagande_närvaro.skapad as skapad
        FROM
            deltagande_närvaro
        INNER JOIN
            deltagare
        ON
            deltagande_närvaro.deltagare_id = deltagare.id
     """ + where)

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return {"närvaro": list(map(to_headers, all.fetchall())), "närvaro_redigerade": {}}
