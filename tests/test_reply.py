import requests


def test_reply_check_email(as_admin, ny_kodstuga):
    id_ = ny_kodstuga["id"]
    deltagare = as_admin.get(
        "http://127.0.0.1:9292/api/deltagare"
    ).json()["deltagare"]
    en_deltagare = [row for row in deltagare if row["kodstuga_id"] == id_][0]
    deltagare_id = en_deltagare["deltagare_id"]
    kontakt_person_id = en_deltagare["kontaktperson_id"]
    kontakt_epost = None
    kontakpersoner = as_admin.get(
        "http://127.0.0.1:9292/api/kontaktpersoner"
    ).json()["kontaktpersoner"]
    for person in kontakpersoner:
        if person["id"] in kontakt_person_id:
            kontakt_epost = person["epost"]
            break
    assert kontakt_epost is not None

    reply_data = {
        "id": [deltagare_id],
        "status": "ja",
        "foto": "ja"
    }
    ret = requests.post("http://127.0.0.1:9292/reply", data=reply_data)
    assert ret.status_code == 200

    emails = as_admin.get(
        "http://127.0.0.1:9292/api/loggar?log=epost"
    ).json()["logdata"]
    assert len([row for row in emails if kontakt_epost in row]) == 1


def test_reply_check_email_inaktiv(as_admin, ny_kodstuga):
    id_ = ny_kodstuga["id"]
    update_data = {
        "id": id_,
        "namn": "Test Kodstuga",
        "sms_text": "Påminnelse om kodstuga.",
        "sms_status": "aktiv",
        "epost_text": "Påminnelse om kodstuga.",
        "epost_rubrik": "Påminnelse om kodstuga",
        "epost_status": "aktiv",
        "epost_text_ja": "Välkommen",
        "epost_rubrik_ja": "Du har nu tackat ja.",
        "epost_status_ja": "inaktiv",
        "typ": "Kodstuga",
        "open": "Ja"
    }
    as_admin.post(
        "http://127.0.0.1:9292/api/kodstugor",
        data=update_data
    )
    deltagare = as_admin.get(
        "http://127.0.0.1:9292/api/deltagare"
    ).json()["deltagare"]
    en_deltagare = [row for row in deltagare if row["kodstuga_id"] == id_][0]
    deltagare_id = en_deltagare["deltagare_id"]
    kontakt_person_id = en_deltagare["kontaktperson_id"]
    kontakt_epost = None
    kontakpersoner = as_admin.get(
        "http://127.0.0.1:9292/api/kontaktpersoner"
    ).json()["kontaktpersoner"]
    for person in kontakpersoner:
        if person["id"] in kontakt_person_id:
            kontakt_epost = person["epost"]
            break
    assert kontakt_epost is not None

    reply_data = {
        "id": [deltagare_id],
        "status": "ja",
        "foto": "ja"
    }
    ret = requests.post("http://127.0.0.1:9292/reply", data=reply_data)
    assert ret.status_code == 200

    emails = as_admin.get(
        "http://127.0.0.1:9292/api/loggar?log=epost"
    ).json()["logdata"]
    assert len([row for row in emails if kontakt_epost in row]) == 0
