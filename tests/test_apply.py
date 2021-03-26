#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests


def test_apply():
    kodstugor = requests.get("http://127.0.0.1:9292/apply/kodstugor")
    kodatuga = kodstugor.json()["kodstugor"][0]
    data = {
        "kodstuga": kodatuga["id"],
        "barn_fornamn": ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"],
        "barn_efternamn": ["Thuresson", "test1a"],
        "klass": ["åk 5", "åk 4"],
        "skola": ["Test", "Test"],
        "kon": ["hon", "hen"],
        "vuxen_fornamn": ["sdfsdf", "jh"],
        "vuxen_efternamn": ["vbhjh", "vbhjh"],
        "email": ["martin.thure@gmail.com", "martin.thure+2@gmail.com"],
        "telefon": ["0723175800", "0723175801"],
        "hittade": "id2",
        "approve": "ja"
    }
    result = requests.post("http://127.0.0.1:9292/api/apply", data=data)
    assert result.status_code == 200


def test_apply_admin(as_admin):
    kodstugor = as_admin.get("http://127.0.0.1:9292/apply/kodstugor")
    kodatuga = kodstugor.json()["kodstugor"][0]
    data = {
        "kodstuga": kodatuga["id"],
        "barn_fornamn": ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"],
        "barn_efternamn": ["Thuresson", "test1a"],
        "klass": ["åk 5", "åk 4"],
        "skola": ["Test", "Test"],
        "foto": ["ja", "nej"],
        "kon": ["hon", "hen"],
        "vuxen_fornamn": ["sdfsdf", "jh"],
        "vuxen_efternamn": ["vbhjh", "vbhjh"],
        "email": ["martin.thure@gmail.com", "martin.thure+2@gmail.com"],
        "telefon": ["0723175800", "0723175801"],
        "hittade": "id2",
        "approve": "ja",
        "invite_now": "ja"
    }
    result = as_admin.post("http://127.0.0.1:9292/api/apply", data=data)
    assert result.status_code == 200


def test_delete_deltagare(as_admin):
    deltagare = as_admin.get("http://127.0.0.1:9292/api/deltagare")
    deleted_count = 0
    for deltagare in deltagare.json()["deltagare"]:
        if deltagare["fornamn"] in ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"]:
            result = as_admin.delete("http://127.0.0.1:9292/api/deltagare", data={"id": deltagare["deltagare_id"]})
            assert result.status_code == 200
            deleted_count = deleted_count + 1
    assert deleted_count == 4


def test_make_scratch(as_admin):
    deltagare = as_admin.get("http://127.0.0.1:9292/api/deltagare")
    for deltagare in deltagare.json()["deltagare"]:
        if deltagare["fornamn"] in ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"]:
            assert deltagare["skonto"] == ""
            assert deltagare["slosen"] == ""
    deltagare = as_admin.get("http://127.0.0.1:9292/api/scratch")
    for deltagare in deltagare.json()["deltagare"]:
        if deltagare["fornamn"] in ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"]:
            assert not deltagare["skonto"] == ""
            assert not deltagare["slosen"] == ""
