#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.parse import parse_qs, quote
import configparser
import requests
from managedata import db
import smtplib
from email.message import EmailMessage
import markdown
import arrow
import hashlib
import requests
from gevent import sleep
import logging
logger = logging.getLogger("tools")

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

class Error400(Exception):
    pass

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

def send_sms(to, message):
    datum = arrow.utcnow().to('Europe/Stockholm').format("YYYY-MM-DD")
    id = hashlib.sha512((to+message+datum).encode("utf-8")).hexdigest()
    try:
        db.cursor.execute('''
            INSERT INTO 
                sms_queue(id, date, till, message, status) 
            VALUES
                (?, ?, ?, ?, ?);
            ''',
            (id, datum, to, message, "köad" )
        )
        db.commit()
    except db.sqlite3.IntegrityError:
        logger.info("SMS redan i kö")

def send_sms_queue():
    while True:
        sleep(2)
        datum = arrow.utcnow().to('Europe/Stockholm').format("YYYY-MM-DD")
        all = db.cursor.execute("""
            SELECT 
                id, till, message
            FROM
                sms_queue
            WHERE
                status = "köad";
        """)
        tosend = all.fetchone()
        if tosend is None:
            continue
        (id, to, message) = tosend

        result = requests.post(
            'https://api.46elks.com/a1/sms',
            auth = (
                config["46elks"]["username"],
                config["46elks"]["password"]
                ),
            data = {
                'from': 'Kodcentrum',
                'to': to,
                'message': message
            }
        )
        db.cursor.execute("""
            UPDATE 
                sms_queue
            SET
                status = "skickad",
                sms_id = ?
            WHERE
                id = ?;
            """,
            (result.json()["id"], id)
        )
        db.commit()

def send_email(to, subject, message):
    datum = arrow.utcnow().to('Europe/Stockholm').format("YYYY-MM-DD")
    id = hashlib.sha512((to+subject+message+datum).encode("utf-8")).hexdigest()
    try:
        db.cursor.execute('''
            INSERT INTO 
                mail_queue(id, date, till, message, status) 
            VALUES
                (?, ?, ?, ?, ?);
            ''',
            (id, datum, to, message, "köad" )
        )
        db.commit()
    except db.sqlite3.IntegrityError:
        logger.info("Epost redan i kö.")

def send_email_queue():
    while True:
        sleep(2)
        datum = arrow.utcnow().to('Europe/Stockholm').format("YYYY-MM-DD")
        all = db.cursor.execute("""
            SELECT 
                id, till, subject, message
            FROM
                mail_queue
            WHERE
                status = "köad";
        """)
        tosend = all.fetchone()
        if tosend is None:
            continue

        (id, to, subject, message) = tosend
        html = markdown.markdown(message)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = "Kodcentrum <hej@kodcentrum.se>"
        msg['To'] = to
        msg.set_content(message)
        msg.add_alternative(html, subtype='html')
        try:
            server = smtplib.SMTP('localhost')
            server.send_message(msg)
            server.quit()
        except:
            logger.error("SMTP send failed.")
            sleep(60*10)
            continue
        db.cursor.execute("""
            UPDATE 
                mail_queue
            SET
                status = "skickad"
            WHERE
                id = ?;
            """,
            (id,)
            )
        db.commit()

