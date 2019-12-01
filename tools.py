#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.parse import parse_qs, quote
import configparser
import requests
from managedata import db
import smtplib
from email.message import EmailMessage
import markdown

def static_file(filename):
    with open(filename, 'r') as content_file:
        imports = content_file.read().split("?>")
        out = ""
        for one_import in imports:
            file = one_import.split("<?")
            if len(file) == 2:
                with open("html/"+file[1], 'r') as importfile:
                    out+=file[0]+importfile.read()
            else:
                out+=file[0]
        return out

class Error404(Exception):
     pass

class Error403(Exception):
    pass

class Error302(Exception):
    pass

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

def url_encode(text):
    return quote(text, safe='')

def set_value(key, value):
    db.cursor.execute('''
        INSERT INTO key_value(key, value) 
        VALUES(?,?)
          ON CONFLICT(key) 
          DO UPDATE SET value=?;''',
          (key,value,value))
    db.commit()

def get_value(key):
    result = db.cursor.execute('''SELECT value FROM key_value WHERE key=?;''', (key,))
    try:
        return result.fetchall()[0][0]
    except:
        return ""

def send_email(to, subject, message):
    html = markdown.markdown(message)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "Kodcentrum <hej@kodcentrum.se>"
    msg['To'] = to
    msg.set_content(message)
    msg.add_alternative(html, subtype='html')

    server = smtplib.SMTP('localhost')
    server.send_message(msg)
    server.quit()