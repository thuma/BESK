#!/usr/bin/env python
# -*- coding: utf-8 -*-
import arrow
from uuid import uuid4
from random import randint


def make_data(namn, extra_data={}):
    post_typer = {
        "kodstuga": {
            "namn": "Test Kodstuga",
            "sms_text": "Påminnelse om kodstuga.",
            "sms_status": "aktiv",
            "epost_text": "Påminnelse om kodstuga.",
            "epost_rubrik": "Påminnelse om kodstuga",
            "epost_status": "aktiv",
            "epost_text_ja": "Välkommen",
            "epost_rubrik_ja": "Du har nu tackat ja.",
            "epost_status_ja": "aktiv",
            "typ": "Kodstuga",
            "open": "Ja"
        },
        "volontar": {
            "namn": "Test Volontär",
            "epost": uuid4().hex + "@none.com",
            "telefon": "07231" + str(randint(10000, 99990)),
            "kodstugor_id": None,
            "roller": "volontär"
        },
        "datum": {
            "kodstugor_id": None,
            "datum": [
                arrow.utcnow().to('Europe/Stockholm').format('YYYY-MM-DD'),
                arrow.utcnow().shift(hours=24).to('Europe/Stockholm').format('YYYY-MM-DD'),
                arrow.utcnow().shift(hours=48).to('Europe/Stockholm').format('YYYY-MM-DD')
            ],
            "typ": [
                "kodstuga",
                "kodstuga",
                "kodstuga"
            ]
        },
        "utskick": {
            "kodstugor_id": None,
            "datum": arrow.utcnow().format('YYYY-MM-DD'),
            "typ": "e-post",
            "status": "aktiv",
            "rubrik": "TEST_ATT_RADERA",
            "text": "Meddelnande som skickas till kontaktpersonen detta datum."
        },
        "kontaktperson": {
            "fornamn": "KP Fornamn",
            "efternamn": "KP Efternamn",
            "epost": uuid4().hex + "@test.com",
            "telefon": "07231" + str(randint(10000, 99990))
        },
        "deltagare": {
            "fornamn": "DT Fornamn",
            "efternamn": "DT Efternamn",
            "status": "ja",
            "kon": "han",
            "foto": "ja",
            "klass": "åk 4",
            "skola": "Stenåken",
            "kodstuga": None,
            "skonto": "",
            "slosen": ""
        },
        "apply": {
            "kodstuga": None,
            "barn_fornamn": ["Test_deltagare_to_be_deleted", "Test2_deltagare_to_be_deleted"],
            "barn_efternamn": ["Thuresson", "test1a"],
            "klass": ["åk 5", "åk 4"],
            "skola": ["Test", "Test"],
            "kon": ["hon", "hen"],
            "vuxen_fornamn": ["sdfsdf", "jh"],
            "vuxen_efternamn": ["vbhjh", "vbhjh"],
            "email": [uuid4().hex + "@test.com", uuid4().hex + "@test.com"],
            "telefon": ["07231" + str(randint(10000, 99990)), "07231" + str(randint(1000, 99990))],
            "hittade": "id2",
            "approve": "ja"
        },
        "apply_admin": {
            "kodstuga": None,
            "barn_fornamn": ["Test Deltagare Förnamn", "Test Deltagare Förnamn 2"],
            "barn_efternamn": ["Test Deltagare Efternamn", "Test Deltagare Efternamn 2"],
            "klass": ["åk 5", "åk 4"],
            "skola": ["Test", "Test"],
            "foto": ["ja", "nej"],
            "kon": ["hon", "hen"],
            "vuxen_fornamn": ["sdfsdf", "jh"],
            "vuxen_efternamn": ["vbhjh", "vbhjh"],
            "email": [uuid4().hex + "@test.com", uuid4().hex + "@test.com"],
            "telefon": ["07231" + str(randint(10000, 99990)), "07231" + str(randint(1000, 99990))],
            "hittade": "id2",
            "approve": "ja",
            "invite_now": "ja"
        },
        "volontarer_plannering": {
            "volontarer_id": None,
            "kodstugor_id": None,
            "datum": arrow.utcnow().format('YYYY-MM-DD'),
            "status": "ja",
            "kommentar": "Meddelande"
        }
    }
    return {**post_typer[namn], **extra_data}
