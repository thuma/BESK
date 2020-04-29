#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import datum


def test_add_send_delete_email(as_admin, ny_kodstuga):
    id_ = ny_kodstuga["id"]
    datum.send_email_reminders_once()
    kontakptersoner = as_admin.get(
        "http://127.0.0.1:9292/api/kontaktpersoner"
    ).json()["kontaktpersoner"]
    emails = as_admin.get(
        "http://127.0.0.1:9292/api/loggar?log=epost"
    ).json()["logdata"]
    found = False
    for kontakperson in kontakptersoner:
        if kontakperson["kodstugor_id"] == id_:

            def hitta(listrad):
                return kontakperson["epost"] in listrad
            assert len(list(filter(hitta, emails))) == 1
            found = True
    assert found


def pest_add_send_delete_sms(as_admin, ny_kodstuga):
    id_ = ny_kodstuga["id"]
    datum.send_sms_reminders_once()
    kontakptersoner = as_admin.get(
        "http://127.0.0.1:9292/api/kontaktpersoner"
    ).json()["kontaktpersoner"]
    sms = as_admin.get(
        "http://127.0.0.1:9292/api/loggar?log=sms"
    ).json()["logdata"]
    found = False
    for kontakperson in kontakptersoner:
        if kontakperson["kodstugor_id"] == id_:

            def hitta(listrad):
                return kontakperson["telefon"] in listrad
            assert len(list(filter(hitta, sms))) == 1
            found = True
    assert found
