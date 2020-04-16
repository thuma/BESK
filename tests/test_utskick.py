#!/usr/bin/env python
# -*- coding: utf-8 -*-
import arrow
from managedata import utskick


def test_add_by_date(as_admin, as_volontär):
    test_kodstuga = False
    kodstugor = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
    for kodstuga in kodstugor.json()["kodstugor"]:
        if kodstuga["namn"] == "Test_Kodstuga":
            test_kodstuga = kodstuga
    data = {
        "kodstugor_id": test_kodstuga['id'],
        "datum": arrow.utcnow().format('YYYY-MM-DD'),
        "typ": "e-post",
        "status": "aktiv",
        "rubrik": "TEST_ATT_RADERA",
        "text": "asdsad"
    }
    utskick_data = as_admin.post("http://127.0.0.1:9292/api/utskick", data=data)
    found = 0
    for one_utskick in utskick_data.json()["utskick"]:
        if one_utskick["rubrik"] == data["rubrik"]:
            found = found + 1
    assert found == 1
    for i in range(0, 20):
        utskick.send_utskick_once()
    utskick_data = as_admin.get("http://127.0.0.1:9292/api/utskick")
    found = 0
    found_data = {}
    for one_utskick in utskick_data.json()["utskick"]:
        if one_utskick["rubrik"] == data["rubrik"] and one_utskick["status"] == 'skickad':
            found = found + 1
            found_data = one_utskick
    assert found == 1
    utskick_data = as_admin.delete("http://127.0.0.1:9292/api/utskick", data=found_data)
    found = 0
    for one_utskick in utskick_data.json()["utskick"]:
        if one_utskick["rubrik"] == data["rubrik"]:
            found = found + 1
    assert found == 0
