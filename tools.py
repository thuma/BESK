#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.parse import parse_qs, quote
import configparser
import requests
from managedata import db
import smtplib
from email.message import EmailMessage
import markdown


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
    msg['From'] = "Kodcentrum <hej@kodcenturm.se>"
    msg['To'] = to
    msg.set_content(message)
    msg.add_alternative(html, subtype='html')

    server = smtplib.SMTP('localhost')
    server.set_debuglevel(1)
    server.sendmsg(msg)
    server.quit()