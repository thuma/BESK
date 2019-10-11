#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent.pywsgi import WSGIServer
from gevent import monkey, sleep
monkey.patch_all()
from urllib.parse import parse_qs
import requests
import sqlite3
import tables
import random
import configparser
import phonenumbers
import json
import uuid
import base64
config = configparser.RawConfigParser()
config.read('../BESK.ini')

verify='../freja.cert'
cert='../BESK.cert'
    
db = sqlite3.connect("../BESK.db")
cursor = db.cursor()

for table in tables.tables:
  db.execute(table)

def application(request, response):
    if request['PATH_INFO'] == '/':
        response('200 OK', [('Content-Type', 'text/html')])
        return [static_file('start.html')]

    elif request['PATH_INFO'] == '/apply':
        if request['REQUEST_METHOD'] == 'POST':
            return [apply(request, response)]         
        response('200 OK', [('Content-Type', 'text/html')])
        return [static_file('apply.html')]

    elif request['PATH_INFO'] == '/login':
        return [login(request, response)]

    elif request['PATH_INFO'] == '/applied':
        response('200 OK', [('Content-Type', 'text/html')])
        return [applied()]        

    elif request['PATH_INFO'] == '/kodstugor':
        response('200 OK', [('Content-Type', 'text/html')])
        return [kodstugor()]
        
    elif request['PATH_INFO'] == '/kontaktpersoner':
        if request['REQUEST_METHOD'] == 'POST':
            return [add_uppdate_kodstuga(request, response)]      
        response('200 OK', [('Content-Type', 'text/html')])
        return [kontaktpersoner()]     

    response('404 Not Found', [('Content-Type', 'text/html')])
    return [b'<h1>Not Found</h1>']

def login():
    data = {
       "userInfoType":"EMAIL",
       "userInfo":"martin.thure@gmail.coms",
       "attributesToReturn":[],
       "minRegistrationLevel":"BASIC"
    }

    data = base64.b64encode(json.dumps(data))
    result = requests.post('https://services.test.frejaeid.com/authentication/1.0/initAuthentication',data={"initAuthRequest":data}, verify=verify, cert=cert)
    authdata = base64.b64encode(result.content)
    laststatus = ""
    while 1:
      sleep(2)
      result2 = requests.post('https://services.test.frejaeid.com/authentication/1.0/getOneResult',data={"getOneAuthResultRequest":authdata}, verify=verify, cert=cert)
      thisstatus = result2.json()["status"]
      if not laststatus == thisstatus:
        laststatus = thisstatus
        print(thisstatus)
      if thisstatus in ("CANCELED","RP_CANCELED","EXPIRED","APPROVED","REJECTED"):
        break
  
def read_post_data(request):
    try:
        body_size = int(request.get('CONTENT_LENGTH', 0))
    except:
        body_size = 0
    request_body = request['wsgi.input'].read(body_size)
    return parse_qs(request_body.decode())

def send_email(to, subject, message):
   url = config['general']['email_url']
   json_data = {"to":to,"subject":subject,"message":message,"key":config['general']['email_key']}
   requests.post(url, json=json_data)

def admin_user(user, password):
    return ( user == config['general']['admin_user']
        and password == config['general']['admin_password'])

def static_file(filename):
    with open(filename, 'rb') as content_file:
        return content_file.read()

def apply(request, response):
    barnid  = []
    vuxid = []
    formdata = read_post_data(request)
    kodstugaid = formdata["kodstuga"][0]
    kodstuga = cursor.execute("""
        SELECT namn
        FROM kodstugor WHERE id = ?;
     """,(kodstugaid,)).fetchall()[0][0];

    for i, value in enumerate(formdata["barn_efternamn"]):
        params = (
        uuid.uuid4().hex,
        kodstugaid,
        formdata["barn_fornamn"][i],
        formdata["barn_efternamn"][i],
        formdata["kon"][i],
        formdata["klass"][i],
        formdata["skola"][i]
        )
        cursor.execute("INSERT INTO deltagare (id,kodstugor_id,fornamn,efternamn,kon,klass,skola) VALUES (?,?,?,?,?,?,?)",params)
        barnid.append(params[0])
    db.commit()
    for i, value in enumerate(formdata["vuxen_efternamn"]):
        params = (
        uuid.uuid4().hex,
        formdata["vuxen_fornamn"][i],
        formdata["vuxen_efternamn"][i],
        formdata["email"][i],
        phonenumbers.format_number(phonenumbers.parse(formdata["telefon"][i], "SE"), phonenumbers.PhoneNumberFormat.E164)
        )
        cursor.execute("INSERT INTO kontaktpersoner (id,fornamn,efternamn,epost,telefon) VALUES (?,?,?,?,?)",params),
        vuxid.append(params[0])
    db.commit()
    hittade = (formdata["hittade"][0],)
    cursor.execute("INSERT INTO hittade (hittade) VALUES (?)", hittade)
    db.commit()
    for vid in vuxid:
      for bid in barnid:
        cursor.execute("INSERT INTO kontaktpersoner_deltagare (kontaktpersoner_id, deltagare_id) VALUES (?,?)",(vid, bid))
    db.commit()
    mailmessage = """Hej!

Vi har mottagit din intresseanmälan till Kodstugan på %kodstuga%
och återkommer till dig via mail så snart vi fördelat platserna. Det finns ett
begränsat antal platser vilket innebär att ditt barn inte är garanterad en plats.
Vi strävar efter en jämn fördelning mellan könen samt att samarbetsskolor har
företräde men utgår annars efter en först till kvarn-princip.

Med vänliga hälsningar,
Kodcentrum
info@kodcentrum.se""".replace("%kodstuga%",kodstuga)
    mailsubject = "Tack för din intresseanmälan"
    for email in formdata["email"]:
        send_email(email, mailsubject, mailmessage)
    
    response('200 OK', [('Content-Type', 'text/html')])
    return b"OK"

def kodstugor():
    all = cursor.execute("""
        SELECT 
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text
        FROM kodstugor;
     """);
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return bytes(json.dumps({"kodstugor":list(map(to_headers, all.fetchall()))}),'utf-8')
    
def add_uppdate_kodstuga(request, response):
    post_data = read_post_data(request)
    if post_data["id"]:
        data = (
            post_data["namn"],
            post_data["sms_text"],
            post_data["epost_text"],
            post_data["epost_rubrik"],
            post_data["id"]
        )
        cursor.execute("""
            UPDATE kodstugor
                SET
                    namn = ?,
                    sms_text = ?,
                    epost_text = ?,
                    epost_rubrik = ?
                WHERE
                    id = ?
            """, data)
        db.commit()
    else:
        data = (
            post_data["namn"],
            post_data["sms_text"],
            post_data["epost_text"],
            post_data["epost_rubrik"],
        )
        cursor.execute("""
            INSERT 
                INTO kodstugor 
                    (namn, sms_text, epost_text, epost_rubrik) 
                VALUES 
                    (?,?,?,?)
            """, data)
        db.commit()
    if request.query.get('id'):
        id = int(request.query.get('id'))
    else:
        id = 0
    all = cursor.execute("""
        SELECT 
            id,
            namn,
            sms_text,
            epost_rubrik,
            epost_text
        FROM kodstugor;
     """)
    response('200 OK', [('Content-Type', 'text/html')])
    return bytes(json.dumps({"kodstugor":list(map(to_headers, all.fetchall()))}),'utf-8')

def kontaktpersoner():
    all = cursor.execute("""
        SELECT 
        	id,
        	fornamn,
 			efternamn,
  			epost,
  			telefon
        FROM
        	kontaktpersoner;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
        return ut
    return bytes(json.dumps({"kontaktpersoner":list(map(to_headers, all.fetchall()))}),'utf-8')

def applied():
    all = cursor.execute("""
        SELECT 
            kodstugor.namn AS kodstuga,
            kodstugor.id AS kodstuga_id,
            deltagare.id AS deltagare_id,
            deltagare.fornamn AS deltagare_fornamn,
            deltagare.efternamn AS deltagare_efternamn,
            deltagare.kon AS deltagare_kon,
            deltagare.skola AS deltagare_skola,
            deltagare.klass AS deltagare_klass,
            GROUP_CONCAT(kontaktpersoner.id,",") AS kontaktperson_id
        FROM deltagare
        INNER JOIN kontaktpersoner_deltagare 
            ON deltagare.id=kontaktpersoner_deltagare.deltagare_id 
        INNER JOIN kontaktpersoner
           ON kontaktpersoner.id=kontaktpersoner_deltagare.kontaktpersoner_id
        INNER JOIN kodstugor
           ON deltagare.kodstugor_id=kodstugor.id
        GROUP BY deltagare.id;
     """)
    def to_headers(row):
        ut = {}
        for idx, col in enumerate(all.description):
            ut[col[0]] = row[idx]
            if col[0] == "kontaktperson_id":
            	ut[col[0]] = ut[col[0]].split(',')
        return ut

    return bytes(json.dumps({"kids":list(map(to_headers, all.fetchall()))}),'utf-8')

if __name__ == '__main__':
    print('Serving on 9191...')
    WSGIServer(('127.0.0.1', 9191), application).serve_forever()