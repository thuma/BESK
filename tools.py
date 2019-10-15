#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.parse import parse_qs
import configparser
import requests

config = configparser.RawConfigParser()
config.read('../BESK.ini')

def read_post_data(request):
    try:
        body_size = int(request.get('CONTENT_LENGTH', 0))
    except:
        body_size = 0
    request_body = request['wsgi.input'].read(body_size)
    return parse_qs(request_body.decode(), keep_blank_values=True)

def read_get_data(request):
    return parse_qs(request['QUERY_STRING'], keep_blank_values=True)

def send_email(to, subject, message):
   url = config['general']['email_url']
   json_data = {"to":to,"subject":subject,"message":message,"key":config['general']['email_key']}
   requests.post(url, json=json_data)