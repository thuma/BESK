#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import requests
from managedata import invite


def test_add(as_admin, as_volontär):
    data = {
        "namn": "Test_Kodstuga_Att_Radera_Vanlig",
        "sms_text": "NEJ",
        "sms_status": "aktiv",
        "epost_text": "Påminnelse Vanlig %kodstuga% %namn%",
        "epost_rubrik": "Påminnelse Vanlig",
        "epost_status": "aktiv",
        "epost_text_ja": "Tack för JA %kodstuga%",
        "epost_rubrik_ja": "Tack för JA",
        "epost_status_ja": "aktiv",
        "typ": "Kodstuga",
        "open": "Ja"
    }
    result = as_admin.post("http://127.0.0.1:9292/api/kodstugor", data=data)
    assert result.status_code == 200
    data = {
        "namn": "Test_Kodstuga_Att_Radera_Lärare",
        "sms_text": "NEJ",
        "sms_status": "aktiv",
        "epost_text": "Påminnelse Lärare %kodstuga% %namn%",
        "epost_rubrik": "Påminnelse Lärare",
        "epost_text_ja": "Tack för JA",
        "epost_status": "aktiv",
        "epost_rubrik_ja": "Tack för JA",
        "epost_status_ja": "aktiv",
        "typ": "Lärarkodstuga",
        "open": "Ja"
    }
    kodstugor = as_admin.post("http://127.0.0.1:9292/api/kodstugor", data=data)
    for kodstuga in kodstugor.json()["kodstugor"]:
        if kodstuga["namn"] == "Test_Kodstuga_Att_Radera_Vanlig":
            vanlig = kodstuga
        elif kodstuga["namn"] == "Test_Kodstuga_Att_Radera_Lärare":
            lärare = kodstuga
    data = {
        "kodstuga": vanlig["id"],
        "barn_fornamn": ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"],
        "barn_efternamn": ["Thuresson", "test1a"],
        "klass": ["åk 5", "åk 4"],
        "skola": ["Test", "Test"],
        "kon": ["hon", "hen"],
        "vuxen_fornamn": ["sdfsdf", "jh"],
        "vuxen_efternamn": ["vbhjh", "vbhjh"],
        "email": [uuid.uuid4().hex + "@test.com", uuid.uuid4().hex + "@test.com"],
        "telefon": ["0723175800", "0723175801"],
        "hittade": "id2",
        "approve": "ja"
    }
    result = requests.post("http://127.0.0.1:9292/api/apply", data=data)
    assert result.status_code == 200
    data_l = {
        "kodstuga": lärare["id"],
        "barn_fornamn": ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"],
        "barn_efternamn": ["Thuresson", "test1a"],
        "klass": ["åk 5", "åk 4"],
        "skola": ["Test", "Test"],
        "kon": ["hon", "hen"],
        "vuxen_fornamn": ["sdfsdf", "jh"],
        "vuxen_efternamn": ["vbhjh", "vbhjh"],
        "email": [uuid.uuid4().hex + "@test.com", uuid.uuid4().hex + "@test.com"],
        "telefon": ["0723175800", "0723175801"],
        "hittade": "id2",
        "approve": "ja"
    }
    result = requests.post("http://127.0.0.1:9292/api/apply", data=data_l)
    assert result.status_code == 200
    for i in range(0, 20):
        invite.send_invites_once()
    result = as_admin.get("http://127.0.0.1:9292/api/loggar?log=epost")
    found = 0
    for logrow in result.json()["logdata"]:
        if data["email"][0] in logrow:
            found = found + 1
        elif data["email"][1] in logrow:
            found = found + 1
    assert found == 2
    found_l = 0
    for logrow in result.json()["logdata"]:
        if data_l["email"][0] in logrow:
            found_l = found_l + 1
        elif data_l["email"][1] in logrow:
            found_l = found_l + 1
    assert found_l == 2

    deltagare = as_admin.get("http://127.0.0.1:9292/api/deltagare").json()["deltagare"]
    invites = []
    for delt in deltagare:
        if (delt["fornamn"] == "Test_deltagare_to_be_deleted" or delt["fornamn"] == "Test2_deltagare_to_be_deleted"):
            invites.append(delt["deltagare_id"])
    assert len(invites) == 4
    invite_result = as_admin.post("http://127.0.0.1:9292/api/invite", data={"invite": invites})
    assert invite_result.status_code == 200
    for i in range(0, 20):
        invite.send_invites_once()
    emaillist = as_admin.get("http://127.0.0.1:9292/api/loggar?log=epost").json()["logdata"]
    found_v = 0
    found_l = 0
    listinfo = []
    for logrow in emaillist:
        if data["email"][0] in logrow and "Erbjudande om plats" in logrow:
            found_v = found_v + 1
            listinfo.append(logrow)
        elif data["email"][1] in logrow and "Erbjudande om plats" in logrow:
            found_v = found_v + 1
            listinfo.append(logrow)
        elif data_l["email"][0] in logrow and "Erbjudande om plats" in logrow:
            found_l = found_l + 1
        elif data_l["email"][1] in logrow and "Erbjudande om plats" in logrow:
            found_l = found_l + 1
    assert found_v == 4
    assert found_l == 4


def test_delete_deltagare(as_admin):
    deltagare = as_admin.get("http://127.0.0.1:9292/api/deltagare")
    deleted_count = 0
    for deltagare in deltagare.json()["deltagare"]:
        if deltagare["fornamn"] in ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"]:
            result = as_admin.delete("http://127.0.0.1:9292/api/deltagare", data={"id": deltagare["deltagare_id"]})
            assert result.status_code == 200
            deleted_count = deleted_count + 1
    assert deleted_count == 4


def test_delete(as_admin, as_volontär):
    result = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
    for one in result.json()['kodstugor']:
        if one["namn"] == "Test_Kodstuga_Att_Radera_Lärare" or one["namn"] == "Test_Kodstuga_Att_Radera_Vanlig":
            result2 = as_admin.delete("http://127.0.0.1:9292/api/kodstugor", data={"id": one["id"]})
            assert result2.status_code == 200
