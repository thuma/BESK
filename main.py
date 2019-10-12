#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent.pywsgi import WSGIServer
from gevent import monkey, sleep
monkey.patch_all()
import requests
import random
import configparser
import phonenumbers
import json
import uuid
import base64
from managedata import db, kodstugor, kontaktpersoner, applied
config = configparser.RawConfigParser()
config.read('../BESK.ini')

verify='../freja.cert'
cert='../BESK.cert'

def generator():
     yield "string"

def to_array_bytes(data):
    if type(data) == type("string"):
        return [data.encode('utf-8')]
    if type(data) == type(b"bytes"):
        return [data]
    if type(data) == type([]):
        return data
    if type(data) == type(generator()):
        return data

def application(request, response):
    return to_array_bytes(route(request, response))

def route(request, response):
    if request['PATH_INFO'].startswith("/api"):
        request['PATH_INFO'] = request['PATH_INFO'][4:]
    if request['PATH_INFO'] == '/':
        response('200 OK', [('Content-Type', 'text/html')])
        return static_file('static/start.html')

    elif request['PATH_INFO'] == '/apply':
        if request['REQUEST_METHOD'] == 'POST':
            return applied.new(request, response)         
        response('200 OK', [('Content-Type', 'text/html')])
        return static_file('static/apply.html')

    elif request['PATH_INFO'] == '/login':
        return login(request, response)

    elif request['PATH_INFO'] == '/applied':
        response('200 OK', [('Content-Type', 'text/html')])
        return applied.all()       

    elif request['PATH_INFO'] == '/kodstugor':
        if request['REQUEST_METHOD'] == 'POST':
            return kodstugor.add_or_uppdate(request, response) 
        response('200 OK', [('Content-Type', 'text/html')])
        return kodstugor.all()
        
    elif request['PATH_INFO'] == '/kontaktpersoner':
        if request['REQUEST_METHOD'] == 'POST':
            return kodstugor.add_or_uppdate(request, response)    
        response('200 OK', [('Content-Type', 'text/html')])
        return kontaktpersoner.all()    

    response('404 Not Found', [('Content-Type', 'text/html')])
    return '<h1>Not Found</h1>'

def admin_user(user, password):
    return ( user == config['general']['admin_user']
        and password == config['general']['admin_password'])

def static_file(filename):
    with open(filename, 'rb') as content_file:
        return content_file.read()

if __name__ == '__main__':
    print('Serving on 9191...')
    WSGIServer(('127.0.0.1', 9191), application).serve_forever()