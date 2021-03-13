#!/usr/bin/env python
# -*- coding: utf-8 -*-
from managedata import datum


def test_send_email_reminder(as_admin, ny_kodstuga):
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
        if id_ in kontakperson["kodstugor_id"]:
            assert len([row for row in emails if kontakperson["epost"] in row]) == 1
            found = True
            break
    assert found


def test_send_email_not_activate(as_admin, ny_kodstuga):
    id_ = ny_kodstuga["id"]
    update_data = {
        "id": id_,
        "namn": "Test Kodstuga",
        "sms_text": "Påminnelse om kodstuga.",
        "sms_status": "aktiv",
        "epost_text": "Påminnelse om kodstuga.",
        "epost_rubrik": "Påminnelse om kodstuga",
        "epost_status": "inaktiv",
        "epost_text_ja": "Välkommen",
        "epost_rubrik_ja": "Du har nu tackat ja.",
        "epost_status_ja": "aktiv",
        "typ": "Kodstuga",
        "open": "Ja"
    }
    as_admin.post(
        "http://127.0.0.1:9292/api/kodstugor",
        data=update_data
    )

    datum.send_email_reminders_once()

    kontakptersoner = as_admin.get(
        "http://127.0.0.1:9292/api/kontaktpersoner"
    ).json()["kontaktpersoner"]
    emails = as_admin.get(
        "http://127.0.0.1:9292/api/loggar?log=epost"
    ).json()["logdata"]
    found = False
    for kontakperson in kontakptersoner:
        if id_ in kontakperson["kodstugor_id"]:
            assert len([row for row in emails if kontakperson["epost"] in row]) == 0
            found = True
            break
    assert found


def test_sms_reminder(as_admin, ny_kodstuga):
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
        if id_ in kontakperson["kodstugor_id"]:
            assert len([row for row in sms if kontakperson["telefon"] in row]) == 1
            found = True
            break
    assert found


def test_sms_reminder_not_activate(as_admin, ny_kodstuga):
    id_ = ny_kodstuga["id"]
    update_data = {
        "id": id_,
        "namn": "Test Kodstuga",
        "sms_text": "Påminnelse om kodstuga.",
        "sms_status": "inaktiv",
        "epost_text": "Påminnelse om kodstuga.",
        "epost_rubrik": "Påminnelse om kodstuga",
        "epost_status": "aktiv",
        "epost_text_ja": "Välkommen",
        "epost_rubrik_ja": "Du har nu tackat ja.",
        "epost_status_ja": "aktiv",
        "typ": "Kodstuga",
        "open": "Ja"
    }
    as_admin.post(
        "http://127.0.0.1:9292/api/kodstugor",
        data=update_data
    )

    datum.send_sms_reminders_once()

    kontakptersoner = as_admin.get(
        "http://127.0.0.1:9292/api/kontaktpersoner"
    ).json()["kontaktpersoner"]
    sms = as_admin.get(
        "http://127.0.0.1:9292/api/loggar?log=sms"
    ).json()["logdata"]
    found = False
    for kontakperson in kontakptersoner:
        if id_ in kontakperson["kodstugor_id"]:
            assert len([row for row in sms if kontakperson["telefon"] in row]) == 0
            found = True
            break
    assert found
