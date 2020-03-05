#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests 

endpoints = [
    '/admin',
    '/loggar',
    '/deltagare',
    '/volontarer/slack',
    '/narvaro',
    '/texter',
    '/invite',
    '/kodstugor',
    '/volontarer',
    '/volontarer_plannering',
    '/utskick',
    '/datum',
    '/kontaktpersoner'
    ]

endpoints200 = [
    '/apply',
    '/reply',
    '/apply/kodstugor'
    ]

def test_all_api(as_admin, as_volontär):
    for path in endpoints:
        data = {}
        result = requests.post("http://127.0.0.1:9292/api"+path, data = data)
        assert result.status_code == 403
        result = requests.get("http://127.0.0.1:9292/api"+path)
        assert result.status_code == 403

def test_all_api_prod(as_admin, as_volontär):
    for path in endpoints:
        data = {}
        result = requests.post("https://besk.kodcentrum.se"+path, data = data)
        assert result.status_code == 403
        result = requests.get("https://besk.kodcentrum.se"+path)
        assert result.status_code == 403
 
def test_all_200(as_admin, as_volontär):
    for path in endpoints200:
        result = requests.get("http://127.0.0.1:9292"+path)
        assert result.status_code == 200
        result = as_admin.get("http://127.0.0.1:9292"+path)
        assert result.status_code == 200
        result = as_volontär.get("http://127.0.0.1:9292"+path)
        assert result.status_code == 200

def test_all_200_prod(as_admin, as_volontär):
    for path in endpoints200:
        result = requests.get("https://besk.kodcentrum.se"+path)
        assert result.status_code == 200

def test_all_302(as_admin, as_volontär):
    for path in ['/login']:
        result = requests.get("http://127.0.0.1:9292"+path, allow_redirects=False)
        assert result.status_code == 302
        result = as_admin.get("http://127.0.0.1:9292"+path, allow_redirects=False)
        assert result.status_code == 302
        result = as_volontär.get("http://127.0.0.1:9292"+path, allow_redirects=False)
        assert result.status_code == 302

def test_all_200or302(as_admin, as_volontär):
    for path in ['/']:
        result = requests.get("http://127.0.0.1:9292"+path, allow_redirects=False)
        assert result.status_code == 302
        result = as_admin.get("http://127.0.0.1:9292"+path, allow_redirects=False)
        assert result.status_code == 200
        result = as_volontär.get("http://127.0.0.1:9292"+path, allow_redirects=False)
        assert result.status_code == 200