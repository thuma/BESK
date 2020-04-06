#!/usr/bin/env python
# -*- coding: utf-8 -*-


def test_add(as_admin, as_volontär):
    data = {
        "namn": "Test_Kodstuga_Att_Radera",
        "sms_text": "",
        "sms_status": "",
        "epost_text": "",
        "epost_rubrik": "",
        "epost_status": "",
        "epost_text_ja": "",
        "epost_rubrik_ja": "",
        "epost_status_ja": "",
        "typ": "Kodstuga",
        "open": "Nej"
    }
    result = as_admin.post("http://127.0.0.1:9292/api/kodstugor", data=data)
    assert result.status_code == 200
    assert result.json()['kodstugor'][0]['id'] > 0


def test_list(as_admin):
    result = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
    assert result.status_code == 200
    assert result.json()['kodstugor'][0]['id'] > 0


def test_update(as_admin):
    result = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
    kodstuga = result.json()['kodstugor'][0]
    if 'typ' not in kodstuga:
        kodstuga['typ'] = "Kodstuga"
    data = {
        "id": kodstuga['id'],
        "namn": kodstuga['namn'],
        "sms_text": kodstuga['sms_text'],
        "sms_status": kodstuga['sms_status'],
        "epost_text": kodstuga['epost_text'],
        "epost_rubrik": kodstuga['epost_rubrik'],
        "epost_status": kodstuga['epost_status'],
        "epost_text_ja": kodstuga['epost_text_ja'],
        "epost_rubrik_ja": kodstuga['epost_rubrik_ja'],
        "epost_status_ja": kodstuga['epost_status_ja'],
        "typ": kodstuga['typ'],
        "open": "Ja"
    }
    result = as_admin.post("http://127.0.0.1:9292/api/kodstugor", data=data)
    for one in result.json()['kodstugor']:
        if one["id"] == data["id"]:
            assert one["namn"] == data["namn"]
            assert one["open"] == data["open"]


def test_delete(as_admin, as_volontär):
    result = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
    for one in result.json()['kodstugor']:
        if one["namn"] == "Test_Kodstuga_Att_Radera":
            result2 = as_admin.delete("http://127.0.0.1:9292/api/kodstugor", data={"id": one["id"]})
            assert result2.status_code == 200
