#!/usr/bin/env python
# -*- coding: utf-8 -*-
import arrow
import pytest

from managedata import datum


def test_add_send_delete_email(as_admin, as_volontär):
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

    id_ = None
    for one in result.json()['kodstugor']:
        if one["namn"] == "Test_Kodstuga_Att_Radera_Vanlig":
            id_ = one["id"]
    if id_ is None:
        pytest.fail("Kan inte hitta id för kodstugoa")

    data = {
        "kodstugor_id": [id_],
        "datum": [arrow.utcnow().shift(hours=24).to('Europe/Stockholm').format('YYYY-MM-DD')],
        "typ": ["kodstuga"]
    }
    result = as_admin.post("http://127.0.0.1:9292/api/datum", data=data)
    assert result.status_code == 200

    datum.send_email_reminders_once()

    result = as_admin.get("http://127.0.0.1:9292/api/loggar?log=epost")
    #assert result.json()["logdata"] is not None
    
    result = as_admin.get("http://127.0.0.1:9292/api/kodstugor")
    for one in result.json()['kodstugor']:
        if one["namn"] == "Test_Kodstuga_Att_Radera_Vanlig":
            result2 = as_admin.delete("http://127.0.0.1:9292/api/kodstugor", data={"id": one["id"]})
            assert result2.status_code == 200


def pest_add_send_delete_sms(as_admin, as_volontär):
    # TODO: ADD reminder to kodstuga
    # TODO: ADD datum for sending
    arrow.utcnow().format("YYYY-MM-DD")
    datum.send_sms_reminders_once()
    # TODO: Check send result
    # TODO: Remove
    assert True
