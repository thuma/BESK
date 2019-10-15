#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import base64
import requests
import configparser
config = configparser.RawConfigParser()
config.read('../BESK.ini')

verify='../freja.cert'
cert='../BESK.cert'

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