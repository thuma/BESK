#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

def test_apply():
    kodstugor = requests.get("http://127.0.0.1:9292/apply/kodstugor")
    kodatuga = kodstugor.json()["kodstugor"][0]
    data = {
        "kodstuga":kodatuga["id"],
        "barn_fornamn":["Martin","tesat"],
        "barn_efternamn":["Thuresson","test1a"],
        "klass":["åk 3","åk 4"],
        "skola":["Test","Test"],
        "kon":["hon","hen"],
        "vuxen_fornamn":["sdfsdf","jh"],
        "vuxen_efternamn":["vbhjh","vbhjh"],
        "email":["martin.thure@gmail.com","martin.thure+2@gmail.com"],
        "telefon":["0723175800","0723175801"],
        "hittade":"id2",
        "approve":"ja"
    }
    result = requests.post("http://127.0.0.1:9292/api/apply", data = data)
    assert result.status_code == 200