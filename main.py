#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()

import json # noqa: 402
import logging # noqa: 402
from logging.handlers import TimedRotatingFileHandler # noqa: 402

from gevent.pywsgi import WSGIServer # noqa: 402
from gevent import spawn, signal, pool # noqa: 402

from tools import ( # noqa: 402
    Error302,
    Error400,
    Error403,
    Error404,
    static_file,
    send_email_queue,
    send_sms_queue
    ) # noqa: 402
from managedata import ( # noqa: 402
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
    texter,
    loggar,
    ) # noqa: 402

rotation_handler = TimedRotatingFileHandler('../BESK.log',
                                            when="D",
                                            interval=1,
                                            backupCount=28)
logging.basicConfig(handlers=[rotation_handler], level=logging.INFO)
logger = logging.getLogger('server')


def convert(data):
    if isinstance(data, dict):
        return json.dumps(data).encode("utf-8")
    return data.encode("utf-8")


def application(request, response):
    try:
        resultdata = convert(route(request))
        if resultdata[0:1] == b"<":
            response('200 OK', [('Content-Type', 'text/html')])
        else:
            response('200 OK', [('Content-Type', 'application/json')])
        return [resultdata]
    except Error302 as error:
        response(error.args[0], error.args[1])
        return [b""]
    except Error400 as error:
        response('400 Bad Request', [('Content-Type', 'text/html')])
        return [str(error).encode('utf-8')]
    except Error403 as error:
        response('403 Forbidden', [('Content-Type', 'text/html')])
        return [str(error).encode('utf-8')]
    except Error404:
        response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>Not Found</h1>']
    except Exception:
        logger.error("SERVER FEL:", exc_info=1)
        response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return ["Ett fel inträffade v.g. kontakta: hej@kodcentrum.se".encode('utf-8')]


def route(request):

    request["BESK_login"] = login.get_login_status(request)

    if request['PATH_INFO'] == '/api/apply':
        return applied.handle(request)
    if request['PATH_INFO'] == '/apply':
        return static_file('static/apply.html')
    if request['PATH_INFO'] == '/reply':
        return invite.reply(request)
    if request['PATH_INFO'] == '/apply/kodstugor':
        return kodstugor.active(request)

    if not request["BESK_login"]["user"] and request['PATH_INFO'] == '/':
        return login.start(request)

    if request['PATH_INFO'] == '/login':
        return login.validate(request)

    if not request["BESK_login"]["user"]:
        raise Error403("You need to login at https://besk.kodcentrum.se/")
    request["BESK_admin"] = login.is_admin(request["BESK_login"]["user"]["user"]["email"])

    if not request["BESK_admin"]:
        if not login.is_approved(request["BESK_login"]["user"]["user"]["email"]):
            raise Error403("Your account has expired.")
        request["BESK_volontarer_id"] = volontarer.get_id(request["BESK_login"]["user"]["user"]["email"])

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

    if request['PATH_INFO'] == '/me':
        return {
            "me": {
                "epost": request["BESK_login"]["user"]["user"]["email"],
                "admin": request["BESK_admin"]
            }
        }

    if request['PATH_INFO'] == '/admin':
        return login.handle_admins(request)

    if request['PATH_INFO'] == '/loggar':
        return loggar.handle(request)

    if request['PATH_INFO'] == '/deltagare':
        return deltagare.handle(request)

    if request['PATH_INFO'] == '/volontarer/slack':
        return volontarer.from_slack(request)

    if request['PATH_INFO'] == '/narvaro':
        return narvaro.handle(request)

    if request['PATH_INFO'] == '/texter':
        return texter.handle(request)

    if request['PATH_INFO'] == '/invite':
        return invite.new(request)

    if request['PATH_INFO'] == '/kodstugor':
        return kodstugor.handle(request)

    if request['PATH_INFO'] == '/volontarer':
        return volontarer.handle(request)

    if request['PATH_INFO'] == '/volontarer_plannering':
        return volontarer_plannering.handle(request)

    if request['PATH_INFO'] == '/utskick':
        return utskick.handle(request)

    if request['PATH_INFO'] == '/datum':
        return datum.handle(request)

    if request['PATH_INFO'] == '/kontaktpersoner':
        return kontaktpersoner.handle(request)

    raise Error404


if __name__ == '__main__':
    print('Serving on 9191...')
    spawn(invite.send_invites)
    spawn(utskick.send_utskick)
    spawn(datum.send_sms_reminders)
    spawn(datum.send_email_reminders)
    spawn(send_email_queue)
    spawn(send_sms_queue)
    green_pool = pool.Pool()
    server = WSGIServer(
        ('127.0.0.1', 9191),
        application,
        spawn=green_pool,
        log=logger,
        error_log=logger
    )

    def shutdown():
        print('Shutting down ...')
        server.close()
        server.stop(timeout=4)
        exit()
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)  # CTRL C
    server.serve_forever(stop_timeout=4)
else:
    green_pool = pool.Pool()
    send_pool = pool.Pool()
    server = WSGIServer(
        ('127.0.0.1', 9292),
        application,
        spawn=green_pool,
        log=logger,
        error_log=logger
    )
