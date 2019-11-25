#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from managedata import tables

db = sqlite3.connect("../BESK.db")
cursor = db.cursor()

def commit():
    db.commit()

for table in tables.tables:
  db.execute(table)