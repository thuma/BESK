#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from managedata import db
from tools import Error400, read_get_data


def handle(request):
    if request['REQUEST_METHOD'] == 'GET':
        return all(request)
    else:
        Error400("Du kan bara visa loggar inte ändra")


def all(request):
    def filterLogs(file):
        if("BESK.log" in file):
            return True
        else:
            return False

    def list_to_string(lista):
        try:
            return ",".join(lista)
        except:  # noqa: E772
            return lista
    if request["BESK_admin"]:
        files = list(filter(filterLogs, os.listdir("../")))
        data = read_get_data(request)
        text = ""
        if "log" in data:
            if data["log"][0] == "sms":
                sms = db.cursor.execute("""
                    SELECT
                        date, till, message, status
                    FROM
                        sms_queue
                    ORDER BY
                        date DESC
                    LIMIT
                        1000;
                """)
                text = list(map(list_to_string, sms.fetchall()))
            elif data["log"][0] == "epost":
                epost = db.cursor.execute("""
                    SELECT
                        date, till, subject, message, status
                    FROM
                        mail_queue
                    ORDER BY
                        date DESC
                    LIMIT
                        1000;
                """)
                text = list(map(list_to_string, epost.fetchall()))
            elif data["log"][0] in files:
                with open("../" + data["log"][0], "r") as logfile:
                    text = logfile.readlines()
        return {"loggar": files, "logdata": text}
    else:
        return {}
