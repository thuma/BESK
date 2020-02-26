#!/usr/bin/env python
# -*- coding: utf-8 -*-
import main
import pytest
import requests
import secrets
from managedata import login

@pytest.fixture(scope="session", autouse=True)
def do_something(request):
    main.server.start()
    request.addfinalizer(finalizer_function)

def finalizer_function():
    main.server.stop()
    main.send_pool.kill()

admin = False
@pytest.fixture
def as_admin():
    global admin
    if not admin:
        email_data = {"user":{"email":"test@test.com"}}
        session = requests.Session()
        key = secrets.token_hex(32)
        login.set_auth(key, email_data)
        cookie_obj = requests.cookies.create_cookie(domain='127.0.0.1',name='session_token',value=key)
        session.cookies.set_cookie(cookie_obj)
        admin = session
        return session
    else:
        return admin

vol = False
@pytest.fixture
def as_volonar(as_admin):
    volontärer = as_admin.get("http://127.0.0.1:9292/api/volontarer").json()["volontärer"]
    found = False
    for volontär in volontärer:
        if volontär["epost"] == "vtest@test.com":
            found = True
    if not found:
        result = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
        kodstugor = result.json()['kodstugor']
        kodstuga = False
        for en_kodstuga in kodstugor:
            if en_kodstuga["namn"] == "Test_Kodstuga":
                kodstuga = en_kodstuga
        
        if not kodstuga:
            data = {
                "namn": "Test_Kodstuga",
                "sms_text":"Påminnelse %namn% %datum%",
                "epost_text":"Påminnelse %namn% %datum% %kodstuga%",
                "epost_rubrik":"Påminnelse",
                "epost_text_ja":"Välkommen %namn% address etc.",
                "epost_rubrik_ja":"Välkommen",
                "typ": "Kodstuga",
                "open":"Ja"
                }
            result = as_admin.post("http://127.0.0.1:9292/api/kodstugor", data = data)
            for en_kodstuga in result.json()['kodstugor']:
                if en_kodstuga["namn"] == "Test_Kodstuga":
                    kodstuga = en_kodstuga
        data = {
            "namn": "Test_Volontär",
            "epost":"vtest@test.com",
            "telefon":"+46723175800",
            "kodstugor_id":kodstuga["id"],
            "roller":"volontär"
            }
        result = as_admin.post("http://127.0.0.1:9292/api/volontarer", data = data)
    global vol
    if not vol:
        email_data = {"user":{"email":"vtest@test.com"}}
        session = requests.Session()
        key = secrets.token_hex(32)
        login.set_auth(key, email_data)
        cookie_obj = requests.cookies.create_cookie(domain='127.0.0.1',name='session_token',value=key)
        session.cookies.set_cookie(cookie_obj)
        vol = session
        return session
    else:
        return vol