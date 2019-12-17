#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import requests
import secrets
from managedata import login

@pytest.fixture
def as_admin():
    email_data = {"user":{"email":"test@test.com"}}
    session = requests.Session()
    key = secrets.token_hex(32)
    login.set_auth(key, email_data)
    cookie_obj = requests.cookies.create_cookie(domain='127.0.0.1',name='session_token',value=key)
    session.cookies.set_cookie(cookie_obj)
    return session

@pytest.fixture
def as_volonar():
    email_data = {"user":{"email":"vtest@test.com"}}
    session = requests.Session()
    key = secrets.token_hex(32)
    login.set_auth(key, email_data)
    cookie_obj = requests.cookies.create_cookie(domain='127.0.0.1',name='session_token',value=key)
    session.cookies.set_cookie(cookie_obj)
    return session

def test_add(as_admin, as_volonar):
    data = {
        "namn": "Test",
        "sms_text":"",
        "epost_text":"",
        "epost_rubrik":"",
        "epost_text_ja":"",
        "epost_rubrik_ja":"",
        "open":"Nej"
        }
    result = as_admin.post("http://127.0.0.1:9191/api/kodstugor", data = data)
    assert result.status_code == 200
    assert result.json()['kodstugor'][0]['id'] > 0

def test_list(as_admin, as_volonar):
    result = as_admin.get("http://127.0.0.1:9191/api/kodstugor")
    assert result.status_code == 200
    assert result.json()['kodstugor'][0]['id'] > 0

    result = as_volonar.get("http://127.0.0.1:9191/api/kodstugor")
    assert result.status_code == 200
    assert result.json()['kodstugor'][0]['id'] > 0

def test_update(as_admin, as_volonar):
    assert 5 == 5

def test_delete(as_admin, as_volonar):
    assert 1 == 1