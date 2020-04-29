#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from managedata import db, login, texter, deltagare
from tools import read_post_data

logger = logging.getLogger("kodstugor")


def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return delete(request)


def delete(request):
    post_data = read_post_data(request)
    if request["BESK_admin"]:
        deltagar_ids = db.cursor.execute("""
            SELECT
                id
            FROM
                deltagare
            WHERE
                kodstugor_id == ?
        """, (post_data['id'][0],)).fetchall()
        for deltagare_id in deltagar_ids:
            deltagare.delete_deltagare(deltagare_id[0])
        db.cursor.execute("""
            DELETE FROM
                utskick
            WHERE
                kodstugor_id = ?
         """, (post_data['id'][0],))
        db.cursor.execute("""
            DELETE FROM
                kodstugor_datum
            WHERE
                kodstugor_id = ?
         """, (post_data['id'][0],))
        db.cursor.execute("""
            DELETE FROM
                volontarer_plannering
            WHERE
                kodstugor_id = ?
         """, (post_data['id'][0],))
        db.cursor.execute("""
            DELETE FROM
                volontarer_roller
            WHERE
                kodstugor_id = ?
         """, (post_data['id'][0],))
        db.cursor.execute("""
            DELETE FROM
                kodstugor
            WHERE
                id = ?
         """, (post_data['id'][0],))
        db.commit()
    return all(request)


def active(request):
    if request["BESK_login"]["user"] and login.is_admin(request["BESK_login"]["user"]["user"]["email"]):
        all = db.cursor.execute("""
            SELECT
                id,
                namn,
                sms_text,
                epost_rubrik,
                epost_text,
                epost_text_ja,
                epost_rubrik_ja,
                typ,
                open,
                sms_status,
                epost_status,
                epost_status_ja
            FROM kodstugor;
         """)
        admin = True
    else:
        all = db.cursor.execute("""
            SELECT
                id,
                namn,
                sms_text,
                epost_rubrik,
                epost_text,
                epost_text_ja,
                epost_rubrik_ja,
                typ,
                open,
                sms_status,
                epost_status,
                epost_status_ja
            FROM kodstugor WHERE open ='Ja';
         """)
        admin = False

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    alla_kodstugor = list(map(to_headers, all.fetchall()))
    return {
        "admin": admin,
        "AnsökanInfo": texter.get_one("Info Vid Ansökan")["text"],
        "kodstugor": alla_kodstugor
    }


def get_kodstuga(kodstua_id):
    all = db.cursor.execute("""
        SELECT
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text,
            epost_text_ja,
            epost_rubrik_ja,
            typ,
            open,
            sms_status,
            epost_status,
            epost_status_ja
        FROM
            kodstugor
        WHERE
            id = ?
     """, (kodstua_id,))

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] in ["sms_status", "epost_status", "epost_status_ja"]:
                ut[col[0]] = row[idx] or "aktiv"
        return ut
    return list(map(to_headers, all.fetchall()))[0]


def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = """
            WHERE
                id
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
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text,
            epost_text_ja,
            epost_rubrik_ja,
            typ,
            open,
            sms_status,
            epost_status,
            epost_status_ja
        FROM kodstugor
     """ + where)

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] in ["sms_status", "epost_status", "epost_status_ja"]:
                ut[col[0]] = row[idx] or "aktiv"
        return ut
    return {"kodstugor": list(map(to_headers, all.fetchall()))}


def add_or_uppdate(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        if "id" in post_data:
            data = (
                post_data["namn"][0],
                post_data["sms_text"][0],
                post_data["epost_text"][0],
                post_data["epost_rubrik"][0],
                post_data["epost_text_ja"][0],
                post_data["epost_rubrik_ja"][0],
                post_data["typ"][0],
                post_data["open"][0],
                post_data["sms_status"][0],
                post_data["epost_status"][0],
                post_data["epost_status_ja"][0],
                post_data["id"][0]
            )
            db.cursor.execute("""
                UPDATE kodstugor
                    SET
                        namn = ?,
                        sms_text = ?,
                        epost_text = ?,
                        epost_rubrik = ?,
                        epost_text_ja = ?,
                        epost_rubrik_ja = ?,
                        typ = ?,
                        open = ?,
                        sms_status = ?,
                        epost_status = ?,
                        epost_status_ja = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                post_data["namn"][0],
                post_data["sms_text"][0],
                post_data["epost_text"][0],
                post_data["epost_rubrik"][0],
                post_data["epost_text_ja"][0],
                post_data["epost_rubrik_ja"][0],
                post_data["typ"][0],
                post_data["open"][0],
                post_data["sms_status"][0],
                post_data["epost_status"][0],
                post_data["epost_status_ja"][0],
            )
            db.cursor.execute("""
                INSERT
                    INTO kodstugor (
                        namn,
                        sms_text,
                        epost_text,
                        epost_rubrik,
                        epost_text_ja,
                        epost_rubrik_ja,
                        typ, open,
                        sms_status,
                        epost_status,
                        epost_status_ja
                        )
                    VALUES
                        (?,?,?,?,?,?,?,?,?,?,?)
                """, data)
        db.commit()
    return all(request)
