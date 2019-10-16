#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import base64
import requests
import configparser
import uuid
from time import time
from managedata import db
from tools import read_get_data, url_encode
config = configparser.RawConfigParser()
config.read('../BESK.ini')

def set_auth(session_id, userdata):
    user_serial_data = json.dumps(userdata)
    expire = int(time()) + (3600 * 12)
    db.cursor.execute('''
        INSERT INTO auth(session_id, user_data, vailid) 
        VALUES(?,?,?)
        ON CONFLICT(session_id) 
        DO UPDATE SET user_data=?, vailid=?;''',
        (session_id,user_serial_data,expire,user_serial_data,expire))
    db.commit()

def get_auth(session_id):
    now = int(time())
    result = db.cursor.execute('''SELECT user_data FROM auth WHERE session_id=? AND vailid > ?;''', (session_id, now))
    try:
        return json.loads(result.fetchall()[0][0])
    except:
        return False

def get_login_status(request):
    session = get_session_token(request)
    return {"user":get_auth(session)}

def get_session_token(request):
    if 'HTTP_COOKIE' in request:
        for cookie in request['HTTP_COOKIE'].split(";"):
            (key, data) = cookie.split("=")
            if key == "session_token":
                return data
    return False

def start(request, response):
    session = get_session_token(request)
    auth_start_url = "https://slack.com/oauth/authorize"+\
        "?scope=identity.basic%20identity.email"+\
        "&client_id=476744412819.789508806369"+\
        "&redirect_uri="+url_encode(config['slack']['redirect_uri'])+\
        "&team=TE0MWC4Q3"
    if not session:
        session_token = uuid.uuid4().hex
        response(
            "302 Found",
            [
                ("Set-Cookie", "session_token="+session_token+"; HttpOnly"), # TODO add Secure
                ("Location", auth_start_url)
            ]
        )
        return "Login"
    else:
        response(
            "302 Found",
            [
                ("Location", auth_start_url)
            ]
        )
        return "Login"

def validate(request, response):
    try:
        query_data = read_get_data(request)
        code = query_data["code"][0]
        accesstoken = requests.get(
            "https://slack.com/api/oauth.access",
            params = {
                "client_id":config['slack']['client_id'],
                "client_secret":config['slack']['client_secret'],
                "code":code,
                "redirect_uri":config['slack']['redirect_uri']}
            )
        userdata = requests.get(
            "https://slack.com/api/users.identity",
            params = {"token":accesstoken.json()["access_token"]}
            )
        session = get_session_token(request)
        set_auth(session, userdata.json())
        response(
            "302 Found",
            [
                ("Location","/")
            ]
        )
        return "Login"
    except Exception as e:
        return start(request, response)

def auth(email):
    verify='../freja.cert'
    cert='../BESK.cert'
    data = {
       "userInfoType":"EMAIL",
       "userInfo":email,
       "attributesToReturn":[],
       "minRegistrationLevel":"BASIC"
    }
    data = base64.b64encode(json.dumps(data))
    result = requests.post(
        'https://services.test.frejaeid.com/authentication/1.0/initAuthentication',
        data={"initAuthRequest":data},
        verify=verify,
        cert=cert
        )
    authList[email] = result.json()
    authdata = base64.b64encode(json.dumps(authList[email]))

    result2 = requests.post(
        'https://services.test.frejaeid.com/authentication/1.0/getOneResult',
        data={"getOneAuthResultRequest":authdata},
        verify=verify,
        cert=cert)
    return result2.json()["status"]