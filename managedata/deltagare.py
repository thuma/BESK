#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import uuid

from tools import read_post_data
from managedata import db, kontaktpersoner

logger = logging.getLogger("deltagare")


def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return delete(request)


def delete_deltagare(deltagare_id):
    db.cursor.execute("""
        DELETE FROM
            klick_svar
        WHERE
            deltagare_id = ?;
        """, (deltagare_id,))
    db.cursor.execute("""
        DELETE FROM
            deltagande_närvaro
        WHERE
            deltagare_id = ?;
        """, (deltagare_id,))
    db.cursor.execute("""
        DELETE FROM
            kontaktpersoner_deltagare
        WHERE
            deltagare_id = ?;
        """, (deltagare_id,))
    db.cursor.execute("""
        DELETE FROM
            deltagare
        WHERE
            id = ?;
        """, (deltagare_id,))
    db.commit()
    db.cursor.execute("""
        DELETE FROM
            kontaktpersoner
        WHERE NOT EXISTS
            (SELECT
                1
            FROM
                kontaktpersoner_deltagare
            WHERE
                kontaktpersoner_deltagare.kontaktpersoner_id = kontaktpersoner.id
            );
        """)
    db.commit()


def delete(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        delete_deltagare(post_data["id"][0])
    utdata = all(request)
    utdata.update(kontaktpersoner.all(request))
    return utdata


def get_kodstuga(id):
    all = db.cursor.execute("""
        SELECT
            kodstugor.id AS id,
            kodstugor.namn AS namn,
            kodstugor.sms_text AS sms_text,
            kodstugor.sms_status AS sms_status,
            kodstugor.epost_rubrik AS epost_rubrik,
            kodstugor.epost_text AS epost_text,
            kodstugor.epost_status AS epost_status,
            kodstugor.epost_text_ja AS epost_text_ja,
            kodstugor.epost_rubrik_ja AS epost_rubrik_ja,
            kodstugor.epost_status_ja AS epost_status_ja,
            kodstugor.open AS open
        FROM
            deltagare
        INNER JOIN
            kodstugor
        ON
           deltagare.kodstugor_id=kodstugor.id
        WHERE
            deltagare.id = ?
        GROUP BY
            deltagare.id
        ORDER BY
            kodstugor.id, deltagare.datum;
     """, (id,))

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return list(map(to_headers, all.fetchall()))[0]


def get_one(id):
    all = db.cursor.execute("""
        SELECT
            kodstugor.id AS kodstuga_id,
            deltagare.id AS deltagare_id,
            deltagare.datum AS datum,
            deltagare.status AS status,
            deltagare.fornamn AS fornamn,
            deltagare.efternamn AS efternamn,
            deltagare.skonto AS skonto,
            deltagare.slosen AS slosen,
            deltagare.kon AS kon,
            deltagare.skola AS skola,
            deltagare.klass AS klass,
            deltagare.foto AS foto,
            GROUP_CONCAT(kontaktpersoner.id,",") AS kontaktperson_id
        FROM deltagare
        LEFT OUTER JOIN kontaktpersoner_deltagare
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id
        LEFT OUTER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        LEFT OUTER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id
        WHERE deltagare.id = ?
        GROUP BY deltagare.id
        ORDER BY kodstugor.id, deltagare.datum;
     """, (id,))

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "kontaktperson_id":
                if ut[col[0]] is None:
                    ut[col[0]] = []
                else:
                    ut[col[0]] = ut[col[0]].split(',')
            if ut[col[0]] is None:
                ut[col[0]] = ""
        return ut
    return list(map(to_headers, all.fetchall()))[0]


def add_or_uppdate(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        if "kontaktperson_id" not in post_data:
            post_data["kontaktperson_id"] = []
        if "id" in post_data:
            data = (
                post_data["fornamn"][0],
                post_data["efternamn"][0],
                post_data["status"][0],
                post_data["kon"][0],
                post_data["foto"][0],
                post_data["klass"][0],
                post_data["skola"][0],
                post_data["kodstuga"][0],
                post_data["skonto"][0],
                post_data["slosen"][0],
                post_data["id"][0]
            )
            db.cursor.execute("""
                UPDATE deltagare
                    SET
                        fornamn = ?,
                        efternamn = ?,
                        status = ?,
                        kon = ?,
                        foto = ?,
                        klass = ?,
                        skola = ?,
                        kodstugor_id = ?,
                        skonto = ?,
                        slosen = ?
                    WHERE
                        id = ?
                """, data)
            db.cursor.execute("""
                DELETE FROM
                    kontaktpersoner_deltagare
                WHERE
                    deltagare_id = ?
                """, (post_data["id"][0], ))
            for kontaktperson_id in post_data["kontaktperson_id"]:
                db.cursor.execute("""
                INSERT
                    INTO kontaktpersoner_deltagare
                        (deltagare_id, kontaktpersoner_id)
                    VALUES
                        (?,?)
                """, (post_data["id"][0], kontaktperson_id))
        else:
            data = (
                uuid.uuid4().hex,
                post_data["fornamn"][0],
                post_data["efternamn"][0],
                post_data["status"][0],
                post_data["kon"][0],
                post_data["klass"][0],
                post_data["skola"][0],
                post_data["kodstuga"][0],
                post_data["skonto"][0],
                post_data["slosen"][0],
            )
            db.cursor.execute("""
                INSERT
                    INTO deltagare
                        (id, fornamn, efternamn, status, kon, klass, skola, kodstugor_id, skonto, slosen)
                    VALUES
                        (?,?,?,?,?,?,?,?,?,?)
                """, data)
            for kontaktperson_id in post_data["kontaktperson_id"]:
                db.cursor.execute("""
                INSERT
                    INTO kontaktpersoner_deltagare
                        (deltagare_id, kontaktpersoner_id)
                    VALUES
                        (?,?)
                """, (data[0], kontaktperson_id))
        db.commit()
    deltagare = all(request)
    deltagare.update(kontaktpersoner.all(request))
    return deltagare


def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = """
            WHERE
                deltagare.status = 'ja'
            AND
                kodstugor.id
            IN (
                SELECT
                    kodstugor_id
                FROM
                    volontarer_roller
                WHERE
                    volontarer_id = %s
            )""" % request["BESK_volontarer_id"]

    all = db.cursor.execute("""
        SELECT
            kodstugor.id AS kodstuga_id,
            deltagare.id AS deltagare_id,
            deltagare.datum AS datum,
            deltagare.status AS status,
            deltagare.fornamn AS fornamn,
            deltagare.efternamn AS efternamn,
            deltagare.skonto AS skonto,
            deltagare.slosen AS slosen,
            deltagare.foto AS foto,
            deltagare.kon AS kon,
            deltagare.skola AS skola,
            deltagare.klass AS klass,
            GROUP_CONCAT(kontaktpersoner.id,",") AS kontaktperson_id
        FROM deltagare
        LEFT OUTER JOIN kontaktpersoner_deltagare
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id
        LEFT OUTER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        LEFT OUTER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id
        %s
        GROUP BY deltagare.id
        ORDER BY kodstugor.id, deltagare.datum;
     """ % where)

    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "kontaktperson_id":
                if ut[col[0]] is None:
                    ut[col[0]] = []
                else:
                    ut[col[0]] = ut[col[0]].split(',')
            if ut[col[0]] is None:
                ut[col[0]] = ""
        return ut

    return {"deltagare": list(map(to_headers, all.fetchall()))}
