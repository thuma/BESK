#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import configparser
import uuid
from time import time

import requests
import logging

from managedata import db
from tools import read_get_data, read_post_data, url_encode, Error302, Error400

config = configparser.RawConfigParser()
config.read('../BESK.ini')

logger = logging.getLogger("login")

def set_auth(session_id, userdata):
    if not session_id or len(session_id) < 31:
        return
    user_serial_data = json.dumps(userdata)
    expire = int(time()) + (3600 * 12)
    db.cursor.execute('''
        INSERT INTO auth(session_id, user_data, vailid)
        VALUES(?,?,?)
        ON CONFLICT(session_id)
        DO UPDATE SET user_data=?, vailid=?;''',
                      (session_id, user_serial_data, expire, user_serial_data, expire))
    db.commit()


def get_auth(session_id):
    if len(session_id) < 32:
        return False
    now = int(time())
    result = db.cursor.execute('''SELECT user_data FROM auth WHERE session_id=? AND vailid > ?;''', (session_id, now))
    try:
        return json.loads(result.fetchone()[0])
    except:  # noqa: E772
        return False


def is_admin(user):
    return user in config['general']['admins']


def handle_admins(request):
    if request['REQUEST_METHOD'] == 'GET':
        return get_admins(request)
    if request['REQUEST_METHOD'] == 'POST':
        return set_admins(request)
    if request['REQUEST_METHOD'] == 'DELETE':
        return get_admins(request)


def get_admins(request):
    config.read('../BESK.ini')
    if not request["BESK_admin"]:
        return {}
    return {"admins": config['general']['admins'].split(",")}


def set_admins(request):
    if not request["BESK_admin"]:
        return {}
    post_data = read_post_data(request)
    new_ini_string = ",".join(post_data["admins"])
    if request["BESK_login"]["user"]["user"]["email"] not in new_ini_string:
        raise Error400("Du kan inte ta bort dig själv.")
    config['general']['admins'] = new_ini_string
    with open('../BESK.ini', 'w') as configfile:
        config.write(configfile)
    return get_admins(request)


def is_approved(user):
    now = int(time())
    result = db.cursor.execute('''SELECT epost FROM volontarer WHERE epost=? AND utdrag_datum > ?;''', (user, now))
    return result.fetchone() is not None


def get_login_status(request):
    session = get_session_token(request)
    if session:
        return {"user": get_auth(session)}
    else:
        return {"user": False}


def get_session_token(request):
    if 'HTTP_COOKIE' in request:
        for cookie in request['HTTP_COOKIE'].split(";"):
            (key, data) = cookie.split("=")
            if key == "session_token":
                return data
    return False


def start(request):
    session = get_session_token(request)
    if "http://localhost" not in config['slack']['redirect_uri']:
        is_secure = "; Secure"
    else:
        is_secure = ""
    auth_start_url = "https://slack.com/oauth/authorize" + \
        "?scope=identity.basic%20identity.email" + \
        "&client_id=" + url_encode(config['slack']['client_id']) + \
        "&redirect_uri=" + url_encode(config['slack']['redirect_uri']) + \
        "&team=TE0MWC4Q3"
    if not session:
        session_token = uuid.uuid4().hex
        raise Error302(
            "302 Found",
            [
                ("Set-Cookie", "session_token=" + session_token + "; HttpOnly" + is_secure),
                ("Location", auth_start_url)
            ]
        )
    else:
        raise Error302(
            "302 Found",
            [
                ("Location", auth_start_url)
            ]
        )


def validate(request):
    try:
        query_data = read_get_data(request)
        code = query_data["code"][0]
        accesstoken = requests.get(
            "https://slack.com/api/oauth.access",
            params={
                "client_id": config['slack']['client_id'],
                "client_secret": config['slack']['client_secret'],
                "code": code,
                "redirect_uri": config['slack']['redirect_uri']}
        )
        userdata = requests.get(
            "https://slack.com/api/users.identity",
            params={"token": accesstoken.json()["access_token"]}
        )
        session = get_session_token(request)
        set_auth(session, userdata.json())
        raise Error302(
            "302 Found",
            [
                ("Location", "/")
            ]
        )
    except Error302 as err:
        raise err
    except Exception:
        logger.error("Login error", exc_info=1)
        return start(request)
