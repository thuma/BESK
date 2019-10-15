#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import base64
import requests
import configparser
import uuid
from managedata import db
from tools import read_get_data
config = configparser.RawConfigParser()
config.read('../BESK.ini')
logedin = {}
verify='../freja.cert'
cert='../BESK.cert'

def get_session_token(request):
    for cookie in request['HTTP_COOKIE'].split(";"):
        (key, data) = cookie.split("=")
        if key == "session_token":
            return data
    return False

def handle(request, response):
    session = get_session_token(request)
    if not session:
        response(
            "302 Found",
            [
                ("Set-Cookie", "session_token="+session_token+"; HttpOnly"), # TODO add Secure
                ("Location","https://slack.com/oauth/authorize?scope=identity.basic%20identity.email&client_id=476744412819.789508806369")
            ]
        )
        return "Login"
    elif session and request['PATH_INFO'] == '/login':
        query_data = read_get_data(request)
        validated = validate(query_data["code"][0])
        response(
            "200 OK",
            [('Content-Type', 'text/html')]
        )
        logedin[session] = validated
        return json.dumps(validated)
    elif session not in logedin:
        response(
            "302 Found",
            [
                ("Location","https://slack.com/oauth/authorize?scope=identity.basic%20identity.email&client_id=476744412819.789508806369")
            ]
        )
        return "Login"
    else:
        response(
            "200 OK",
            [('Content-Type', 'text/html')]
        )
        return json.dumps(logedin[session])

def validate(code):
    accesstoken = requests.get(
        "https://slack.com/api/oauth.access",
        params = {
            "client_id":config['slack']['client_id'],
            "client_secret":config['slack']['client_secret'],
            "code":code}
        )

    userdata = requests.get(
        "https://slack.com/api/users.identity",
        params = {"token":accesstoken.json()["access_token"]}
        )
    return userdata.json()

def auth(email):
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