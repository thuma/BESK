#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent.pywsgi import WSGIServer
from gevent import monkey, sleep, spawn
monkey.patch_all()
import requests
import random
import json
import base64
from managedata import (
    db,
    kodstugor,
    kontaktpersoner,
    applied,
    datum,
    login,
    invite,
    volontarer,
    volontarer_plannering,
    utskick,
    deltagare,
    narvaro,
    texter
    )

class Error404(Exception):
     pass

class Error403(Exception):
    pass

def generator():
     yield "string"

def convert(data):
    if type(data) == type({}):
        return json.dumps(data)
    elif type(data) == type("string"):
        return data.encode()
    elif type(data) == type([]):
        return json.dumps(data)

def application(request, response):
    try:
        resultdata = convert(route(request))
        if resultdata[0:1] == b"<":
            response('200 OK', [('Content-Type', 'text/html')])
        else:
            response('200 OK', [('Content-Type', 'application/json')])
        return [resultdata]
    except Error403 as error:
        response('403 Forbidden', [('Content-Type', 'text/html')])
        return [str(error).encode('utf-8')]
    except Error404 as error:
        response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>Not Found</h1>']
    except Exception as error:
        response('400 Bad Request', [('Content-Type', 'text/html')])
        return [str(error).encode('utf-8')]

def route(request):
    if request['PATH_INFO'] == '/api/apply':
        return applied.handle(request)
    elif request['PATH_INFO'] == '/apply':
        return static_file('static/apply.html')
    elif request['PATH_INFO'] == '/reply':
        return invite.handle(request)
    elif request['PATH_INFO'] == '/apply/kodstugor':
        return kodstugor.active(request)

    request["BESK_login"] = login.get_login_status(request)

    if request["BESK_login"]["user"] == False and request['PATH_INFO'] == '/':
        return login.start(request, response)

    if request['PATH_INFO'] == '/login':
        return login.validate(request)

    if request["BESK_login"]["user"] == False:
        raise Error403("You need to login at https://besk.kodcentrum.se/")
    else:
        request["BESK_admin"] = login.is_admin(request["BESK_login"]["user"]["user"]["email"])

    if not request["BESK_admin"]:
        if not login.is_approved(request["BESK_login"]["user"]["user"]["email"]):
            raise Error403("Your account has expired.")

    if request['PATH_INFO'] == '/':
        return static_file('static/start.html')

    if request['PATH_INFO'] == '/index.js':
        return static_file('static/index.js')

    if request['PATH_INFO'].startswith("/api"):
        request['PATH_INFO'] = request['PATH_INFO'][4:]

    ######################################################################
    #                                                                    #
    #                         API endpoints                              #
    #                                                                    #
    ######################################################################

    if request['PATH_INFO'] == '/deltagare':
        return deltagare.handle(request) 

    if request['PATH_INFO'] == '/volontarer/slack':
        return volontarer.handle_slack(request)

    if request['PATH_INFO'] == '/narvaro':
        return narvaro.handle(request) 

    if request['PATH_INFO'] == '/texter':
        return texter.handle(request)

    elif request['PATH_INFO'] == '/invite':
        return invite.handle(request)

    elif request['PATH_INFO'] == '/kodstugor':
        return kodstugor.handle(request) 

    elif request['PATH_INFO'] == '/volontarer':
        return volontarer.handle(request)

    elif request['PATH_INFO'] == '/volontarer_plannering':
        return volontarer_plannering.handle(request)
        
    elif request['PATH_INFO'] == '/utskick':
        return utskick.handle(request)

    elif request['PATH_INFO'] == '/datum':
        return datum.handle(request) 
        
    elif request['PATH_INFO'] == '/kontaktpersoner':
        return kontaktpersoner.handle(request)

    raise Error404

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

if __name__ == '__main__':
    spawn(invite.send_invites)
    print('Serving on 9191...')
    WSGIServer(('127.0.0.1', 9191), application).serve_forever()