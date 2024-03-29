#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import configparser
import smtplib
import hashlib
from urllib.parse import parse_qs, quote
from email.message import EmailMessage

import requests
import markdown
import arrow
from gevent import sleep

from managedata import db

logger = logging.getLogger("tools")


def static_file(filename):
    with open(filename, 'r') as content_file:
        imports = content_file.read().split("?>")
        out = ""
        for one_import in imports:
            file = one_import.split("<?")
            if len(file) == 2:
                with open("html/" + file[1], 'r') as importfile:
                    out += file[0] + importfile.read()
            else:
                out += file[0]
        return out


def static_files(filename):
    with open(filename, 'r') as content_file:
        return content_file.read()


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
    except Exception:
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
                      (key, value, value))
    db.commit()


def get_value(key):
    result = db.cursor.execute('''SELECT value FROM key_value WHERE key=?;''', (key,))
    try:
        return result.fetchall()[0][0]
    except Exception:
        return ""


def send_sms(receiver, message):
    if len(message.strip()) < 4:
        return
    datum = arrow.utcnow().to('Europe/Stockholm').format("YYYY-MM-DD")
    id = hashlib.sha512((receiver + message + datum).encode("utf-8")).hexdigest()
    try:
        db.cursor.execute('''
            INSERT INTO
                sms_queue(id, date, till, message, status)
            VALUES
                (?, ?, ?, ?, ?);
            ''',
                          (id, datum, receiver, message, "köad"))
        db.commit()
    except db.sqlite3.IntegrityError:
        logger.info("SMS redan i kö")
    except Exception:
        logger.error("SMS kunde inte skickas till: " + receiver, exc_info=1)


def send_sms_queue():
    while True:
        try:
            sleep(2)
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
                auth=(
                    config["46elks"]["username"],
                    config["46elks"]["password"]
                ),
                data={
                    'from': 'Kodcentrum',
                    'to': to,
                    'message': message
                }
            )
            try:
                sms_id = result.json()["id"]
            except Exception:
                sms_id = "error"
            db.cursor.execute("""
                UPDATE
                    sms_queue
                SET
                    status = "skickad",
                    sms_id = ?
                WHERE
                    id = ?;
                """,
                              (sms_id, id))
            db.commit()
        except Exception:
            logger.error("Epost kunde inte skickas från kön.", exc_info=1)
            sleep(3600)


def send_email(to, subject, message):
    if len(message.strip()) < 4:
        return
    datum = arrow.utcnow().to('Europe/Stockholm').format("YYYY-MM-DD")
    id = hashlib.sha512((to + subject + message + datum).encode("utf-8")).hexdigest()
    try:
        db.cursor.execute('''
            INSERT INTO
                mail_queue(id, date, till, subject, message, status)
            VALUES
                (?, ?, ?, ?, ?, ?);
            ''',
                          (id, datum, to, subject, message, "köad"))
        db.commit()
    except db.sqlite3.IntegrityError:
        logger.info("Epost redan i kö.")
    except Exception:
        logger.error("Epost kunde inte skickas till: " + to, exc_info=1)


def send_mail_to_office365(to, subject, message):
    html = markdown.markdown(message)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "Kodcentrum <hej@kodcentrum.se>"
    msg['To'] = to
    msg.set_content(message)
    msg.add_alternative(html, subtype='html')
    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.login(config["office365"]["email"], config["office365"]["password"])
        server.send_message(msg)
        server.quit()
        return True
    except smtplib.SMTPNotSupportedError:
        logger.error("SMTPNotSupportedError to: " + to, exc_info=1)
        return False
    except smtplib.SMTPDataError:
        logger.error("SMTPDataError to: " + to, exc_info=1)
        return False
    except smtplib.SMTPRecipientsRefused:
        logger.error("SMTPRecipientsRefused to: " + to, exc_info=1)
        return False
    except smtplib.SMTPSenderRefused:
        logger.error("SMTPSenderRefused to: " + to, exc_info=1)
        return False
    except Exception:
        logger.error("SMTP send failed to: " + to, exc_info=1)
        return "retry"


def send_email_queue():
    while True:
        try:
            sleep(2)
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
            mail_sent = send_mail_to_office365(to, subject, message)
            if not mail_sent:
                db.cursor.execute("""
                UPDATE
                    mail_queue
                SET
                    status = "kunde inte skickas"
                WHERE
                    id = ?;
                """,
                                  (id,))
                db.commit()
                continue
            if mail_sent == "retry":
                sleep(3600)
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
        except Exception:
            logger.error("Epost kunde inte skickas från kön.", exc_info=1)
            sleep(3600)
