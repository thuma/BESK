#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import db
from tools import read_post_data, config
import json
import phonenumbers
import requests
import datetime
import time

def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    if request['REQUEST_METHOD'] == 'POST':
        return add_or_uppdate(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return delete(request)

def get_kodstuga(epost):
    all = db.cursor.execute("""
        SELECT 
            kodstugor_id
        FROM 
            volontarer 
        WHERE 
            epost = ?;
     """, (epost,));
    return all.fetchall()[0][0]

def all(request):
    if request["BESK_admin"]:
        where = ""
    else:
        where = "WHERE kodstugor_id = " + str(request["BESK_kodstuga"])
    all = db.cursor.execute("""
        SELECT 
            id,
            kodstugor_id,
            epost,
            namn,
            telefon,
            utdrag_datum
        FROM volontarer 
     """ + where + """ ORDER BY kodstugor_id """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            if col[0] == "utdrag_datum" and isinstance(row[idx], int):
                ut[col[0]] = int_to_date(row[idx])
            else:
                ut[col[0]] = row[idx]
        return ut
    return {"volontärer":list(map(to_headers, all.fetchall()))}

def delete(request):
    post_data = read_post_data(request)
    db.cursor.execute("""
        DELETE FROM 
            volontarer
        WHERE 
            epost = ?
     """,(post_data['epost'][0],))
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

def add_or_uppdate(request):
    post_data = read_post_data(request)
    if "flytta" in post_data:
        for flytta_id in post_data["flytta"]:
            db.cursor.execute("""
                UPDATE volontarer
                    SET
                        kodstugor_id = ?
                    WHERE
                        id = ?
                """, (post_data["kodstugor_id"][0], flytta_id))
    elif "flera" in post_data:
        for i, namn in enumerate(post_data["namn"]):
            data = (
                post_data["namn"][i],
                post_data["epost"][i],
                phonenumber_to_format(post_data["telefon"][i]),
                post_data["kodstugor_id"][0],
                date_to_int(post_data["utdrag_datum"][i]),
            )
            try:
                db.cursor.execute("""
                    INSERT 
                        INTO volontarer
                            (namn, epost, telefon, kodstugor_id, utdrag_datum) 
                        VALUES 
                            (?,?,?,?,?)
                    """, data)
            except db.sqlite3.IntegrityError:
                pass
    else:
        try:
            phone_number = phonenumbers.parse(post_data["telefon"][0], "SE")
            phone_number_str = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        except:
            raise Exception("Fyll i ett giltigt telefonummer.")
        if not phonenumbers.is_valid_number(phone_number):
            raise Exception("Fyll i ett giltigt telefonummer.")
        if "id" in post_data:
            data = (
                post_data["namn"][0],
                post_data["epost"][0],
                phone_number_str,
                post_data["kodstugor_id"][0],
                date_to_int(post_data["utdrag_datum"][0]),
                post_data["id"][0]
            )
            db.cursor.execute("""
                UPDATE volontarer
                    SET
                        namn = ?,
                        epost = ?,
                        telefon = ?,
                        kodstugor_id = ?,
                        utdrag_datum = ?
                    WHERE
                        id = ?
                """, data)
        else:
            data = (
                post_data["namn"][0],
                post_data["epost"][0],
                phone_number_str,
                post_data["kodstugor_id"][0],
                date_to_int(post_data["utdrag_datum"][0]),
            )
            try:
                db.cursor.execute("""
                    INSERT 
                        INTO volontarer
                            (namn, epost, telefon, kodstugor_id, utdrag_datum) 
                        VALUES 
                            (?,?,?,?,?)
                    """, data)
            except db.sqlite3.IntegrityError:
                 raise Exception("E-Postadressen finns redan.")
    db.commit()
    return all(request)