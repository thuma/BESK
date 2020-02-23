#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db, texter
from tools import read_post_data, config, Error400, send_email
import json
import phonenumbers
import requests
import datetime
import time
import arrow
import logging
logger = logging.getLogger("volontärer")

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return delete(request)

def get_by_id(volid):
    all = db.cursor.execute("""
        SELECT 
            id,
            epost,
            namn,
            telefon
        FROM
            volontarer 
        WHERE
            id = ?
        LIMIT 1""", (volid, ));
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            if col[0] == "utdrag_datum" and isinstance(row[idx], int):
                ut[col[0]] = arrow.Arrow.utcfromtimestamp(row[idx]).format("YYYY-MM-DD")
            else:
                ut[col[0]] = row[idx]
        return ut
    return to_headers(all.fetchone())

def get_id(epost):
    all = db.cursor.execute("""
        SELECT 
            id
        FROM 
            volontarer 
        WHERE 
            epost = ?;
     """, (epost,));
    return all.fetchone()[0]

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = """
            WHERE 
                volontarer.id
            IN (
                SELECT 
                    volontarer_id 
                FROM 
                    volontarer_roller
                WHERE 
                    kodstugor_id
                IN (
                    SELECT
                        kodstugor_id
                    FROM
                        volontarer_roller
                    WHERE
                        volontarer_id = %s
                )
            ) """ % request["BESK_volontarer_id"]
    all = db.cursor.execute("""
        SELECT 
            volontarer.id as id,
            volontarer.epost as epost,
            volontarer.namn as namn,
            volontarer.telefon as telefon,
            volontarer.utdrag_datum as utdrag_datum,
            group_concat(volontarer_roller.kodstugor_id) as kodstugor_id,
            group_concat(volontarer_roller.roll) as roller
        FROM 
            volontarer
        LEFT OUTER JOIN 
            volontarer_roller
        ON 
            volontarer.id = volontarer_roller.volontarer_id
        %s
        GROUP BY
            volontarer.id
    """ % where );
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            if col[0] == "utdrag_datum" and isinstance(row[idx], int):
                ut[col[0]] = arrow.Arrow.utcfromtimestamp(row[idx]).format("YYYY-MM-DD")
            elif col[0] == "kodstugor_id":
                try:
                    ut[col[0]] = list(map(int, row[idx].split(",")))
                except:
                    ut[col[0]] = []
            elif col[0] == "roller":
                try:
                    ut[col[0]] = row[idx].split(",")
                except:
                    ut[col[0]] = []
            else:
                ut[col[0]] = row[idx]
        return ut
    return {"volontärer":list(map(to_headers, all.fetchall()))}

def delete(request):
    if request["BESK_admin"]:
        post_data = read_post_data(request)
        db.cursor.execute("""
            DELETE FROM 
                volontarer_plannering
            WHERE 
                volontarer_id = ?
            """,(post_data['id'][0],))
        db.cursor.execute("""
            DELETE FROM 
                volontarer_roller
            WHERE 
                volontarer_id = ?
            """,(post_data['id'][0],))
        db.cursor.execute("""
            DELETE FROM 
                volontarer
            WHERE 
                id = ?
            """,(post_data['id'][0],))
        db.commit()
    return all(request)

slack_members = []

def from_slack(request):
    if request["BESK_admin"]:
        result = requests.get("https://slack.com/api/users.list?limit=999&token="+config['slack']['token'])
        def basicdata(member):
            return {"selected":False,"slack_id":member["id"],"namn":member["profile"]["real_name"],"epost":member["profile"]["email"],"telefon":phonenumber_to_format(member["profile"]["phone"])}
        def filterusers(member):
            return "email" in member["profile"]
        return {"volontärer_slack":list(map(basicdata,filter(filterusers,result.json()["members"])))}
    else:
        return {"volontärer_slack":[]}

def phonenumber_to_format(number):
    try:
        phone_number = phonenumbers.parse(number, "SE")
        return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
    except:
        return "+46700000000"

def date_to_int(date_text):
    return time.mktime(datetime.datetime.strptime(date_text, '%Y-%m-%d').timetuple())

def int_to_date(int):
    return datetime.datetime.utcfromtimestamp(int).strftime('%Y-%m-%d')

def add_roller(kodstugor_id, roll, volontarer_id):
    db.cursor.execute("""
        INSERT INTO
            volontarer_roller (
                kodstugor_id,
                roll,
                volontarer_id
            )
        VALUES
            (?, ?, ?);
        """, (kodstugor_id, roll, volontarer_id))
    db.commit()

def add_or_update_roller(kodstugor_roll_list, volontarer_id):
    db.cursor.execute("""
        DELETE FROM
            volontarer_roller
        WHERE
            volontarer_id = ?
        """, (volontarer_id,))
    db.commit()
    for roll in kodstugor_roll_list:
        db.cursor.execute("""
            INSERT INTO
                volontarer_roller (
                    kodstugor_id,
                    roll,
                    volontarer_id
                )
            VALUES
                (?, ?, ?);
            """, (roll['kodstugor_id'], roll['roll'], volontarer_id))
        db.commit()

def add_or_update_admin(request):
    post_data = read_post_data(request)
    if "flytta" in post_data:
        for flytta_id in post_data["flytta"]:
            add_roller(post_data["kodstugor_id"][0], "volontär", flytta_id)
    elif "flera" in post_data:
        for i, namn in enumerate(post_data["namn"]):
            data = (
                post_data["namn"][i],
                post_data["epost"][i],
                phonenumber_to_format(post_data["telefon"][i]),
                arrow.get("2090-01-01").timestamp,
            )
            try:
                db.cursor.execute("""
                    INSERT 
                        INTO volontarer
                            (namn, epost, telefon, utdrag_datum) 
                        VALUES 
                            (?,?,?,?)
                    """, data)
                
                db.commit()
                add_roller(
                    post_data["kodstugor_id"][0],
                    "volontär",
                    get_id(post_data["epost"][i])
                    )
                send_email(post_data["epost"][i], "BESK-konto aktiverat", texter.get_one("BESK-konto aktiverat")["text"])
            except db.sqlite3.IntegrityError:
                pass
    else:
        try:
            phone_number = phonenumbers.parse(post_data["telefon"][0], "SE")
            phone_number_str = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        except:
            raise Error400("Fyll i ett giltigt telefonummer.")
        if not phonenumbers.is_valid_number(phone_number):
            raise Error400("Fyll i ett giltigt telefonummer.")
        if "id" in post_data:
            data = (
                post_data["namn"][0],
                post_data["epost"][0],
                phone_number_str,
                arrow.get("2090-01-01").timestamp,
                post_data["id"][0]
            )
            db.cursor.execute("""
                UPDATE volontarer
                    SET
                        namn = ?,
                        epost = ?,
                        telefon = ?,
                        utdrag_datum = ?
                    WHERE
                        id = ?
                """, data)
            db.commit()
            roll_list = []
            for form_index, value in enumerate(post_data["kodstugor_id"]):
                roll_list.append(
                    {
                    "kodstugor_id": value,
                    "roll": post_data["roll"][form_index]
                    }
                );
            add_or_update_roller(roll_list, post_data["id"][0])
        else:
            data = (
                post_data["namn"][0],
                post_data["epost"][0],
                phone_number_str,
                arrow.get("2090-01-01").timestamp,
            )
            try:
                db.cursor.execute("""
                    INSERT 
                        INTO volontarer
                            (namn, epost, telefon, utdrag_datum) 
                        VALUES 
                            (?,?,?,?)
                    """, data)
                db.commit()
                send_email(post_data["epost"][0], "BESK-konto aktiverat", texter.get_one("BESK-konto aktiverat")["text"])
                roll_list = []
                for form_index, value in enumerate(post_data["kodstugor_id"]):
                    roll_list.append(
                        {
                        "kodstugor_id": value,
                        "roll": post_data["roll"][form_index]
                        }
                    );
                add_or_update_roller(roll_list, get_id(post_data["epost"][0]))
            except db.sqlite3.IntegrityError:
                 raise Error400("E-Postadressen finns redan.")

def update_as_vol(request):
    post_data = read_post_data(request)
    if not get_by_id(post_data["id"][0])["epost"] == request["BESK_login"]["user"]["user"]["email"]:
        return
    try:
        phone_number = phonenumbers.parse(post_data["telefon"][0], "SE")
        phone_number_str = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
    except:
        raise Error400("Fyll i ett giltigt telefonummer.")
    if not phonenumbers.is_valid_number(phone_number):
        raise Error400("Fyll i ett giltigt telefonummer.")
    if "id" in post_data:
        data = (
            post_data["namn"][0],
            phone_number_str,
            post_data["id"][0]
        )
        db.cursor.execute("""
            UPDATE volontarer
                SET
                    namn = ?,
                    telefon = ?
                WHERE
                    id = ?
            """, data)
    db.commit()

def add_or_uppdate(request):
    if request["BESK_admin"]:
        add_or_update_admin(request)
    else:
        update_as_vol(request)
    return all(request)