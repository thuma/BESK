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
def as_volonar():
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