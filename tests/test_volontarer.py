#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import random

def test_add(as_admin, as_volonar):
    result = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
    kodstuga = result.json()['kodstugor'][0]
    data = {
        "namn": "Test_Volontär_Att_Radera",
        "epost":"test-running-remove"+str(random())+"@none.com",
        "telefon":"0723175800",
        "kodstugor_id":kodstuga["id"]
        }
    result = as_admin.post("http://127.0.0.1:9292/api/volontarer", data = data)
    assert result.status_code == 200
    found = False
    for volontar in result.json()['volontärer']:
        if volontar["namn"] == "Test_Volontär_Att_Radera":
            found = True
    assert found

def test_list(as_admin, as_volonar):
    result = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
    assert result.status_code == 200
    assert result.json()['kodstugor'][0]['id'] > 0

def test_update(as_admin, as_volonar):
    result = as_admin.get("http://127.0.0.1:9292/api/volontarer")
    for volontar in result.json()['volontärer']:
        if volontar["namn"] == "Test_Volontär_Att_Radera":
            data = {
            "namn": volontar["namn"],
            "epost":"ändrad"+str(random())+"@gmail.com",
            "telefon":"+46723175708",
            "id":volontar["id"],
            "kodstugor_id":volontar["kodstugor_id"]
            }
            result2 = as_admin.post("http://127.0.0.1:9292/api/volontarer", data = data)
            assert result2.status_code == 200
            for one in result2.json()['volontärer']:
                if one["id"] == data["id"]:
                    assert one["epost"] == data["epost"]
                    assert one["telefon"] == data["telefon"]

def test_delete(as_admin, as_volonar):
    result = as_volonar.get("http://127.0.0.1:9292/api/volontarer")
    for volontar in result.json()['volontärer']:
        if volontar["namn"] == "Test_Volontär_Att_Radera":
            result2 = as_volonar.delete("http://127.0.0.1:9292/api/volontarer", data = {"id":volontar["id"]})
            assert result2.status_code == 200
    result = as_volonar.get("http://127.0.0.1:9292/api/volontarer")
    found = False
    for volontar in result.json()['volontärer']:
        if volontar["namn"] == "Test_Volontär_Att_Radera":
            found = True
    assert found
    result = as_admin.get("http://127.0.0.1:9292/api/volontarer")
    for volontar in result.json()['volontärer']:
        if volontar["namn"] == "Test_Volontär_Att_Radera":
            result2 = as_admin.delete("http://127.0.0.1:9292/api/volontarer", data = {"id":volontar["id"]})
            assert result2.status_code == 200
    result = as_admin.get("http://127.0.0.1:9292/api/volontarer")
    found = False
    for volontar in result.json()['volontärer']:
        if volontar["namn"] == "Test_Volontär_Att_Radera":
            found = True
    assert found == False