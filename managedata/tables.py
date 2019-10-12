#!/usr/bin/env python
# -*- coding: utf-8 -*-

tables = ['''
  CREATE TABLE IF NOT EXISTS kodstugor (
  id INTEGER PRIMARY KEY,
  namn TEXT,
  sms_text TEXT,
  epost_text TEXT,
  epost_rubrik TEXT );
''',
'''
  CREATE TABLE IF NOT EXISTS hittade (
  hittade TEXT);
''',
'''
CREATE TABLE IF NOT EXISTS kodstugor_datum (
  id INTEGER PRIMARY KEY,
  kodstugor_id INT,
  datum TEXT,
  typ TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  ); 
''',
'''
CREATE INDEX IF NOT EXISTS kodstugor_datum_kodstugor_id ON kodstugor_datum(kodstugor_id);
''',
'''
CREATE TABLE IF NOT EXISTS deltagare (
  id TEXT PRIMARY KEY,
  kodstugor_id INT,
  fornamn TEXT,
  efternamn TEXT,
  kon TEXT,
  skola TEXT,
  klass TEXT,
  foto TEXT,
  frannummer TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  ); 
''',
'''
CREATE TABLE IF NOT EXISTS kontaktpersoner (
  id TEXT PRIMARY KEY,
  fornamn TEXT,
  efternamn TEXT,
  epost TEXT,
  telefon TEXT);
''',
'''
CREATE TABLE IF NOT EXISTS kontaktpersoner_deltagare (
  id INTEGER PRIMARY KEY,
  kontaktpersoner_id INT,
  deltagare_id INT,
  FOREIGN KEY(kontaktpersoner_id) REFERENCES kontaktpersoner(id),
  FOREIGN KEY(deltagare_id) REFERENCES deltagare(id)
  ); 
''',
'''
CREATE TABLE IF NOT EXISTS deltagande (
  id INTEGER PRIMARY KEY,
  kodstugor_id INT,
  deltagare_id INT,
  status TEXT,
  datum TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id),
  FOREIGN KEY(deltagare_id) REFERENCES deltagare(id)
  ); 
''',
'''
CREATE TABLE IF NOT EXISTS kick_svar (
  id INTEGER PRIMARY KEY,
  deltagare_id INT,
  svar TEXT,
  datum TEXT,
  FOREIGN KEY(deltagare_id) REFERENCES deltagare(id)
  ); 
''',
'''
CREATE TABLE IF NOT EXISTS sms_svar (
  id INTEGER PRIMARY KEY,
  fran TEXT,
  till TEXT,
  text TEXT,
  datum TEXT); 
''',
'''
CREATE TABLE IF NOT EXISTS utskick (
  id INTEGER PRIMARY KEY,
  kodstugor_id INT,
  typ TEXT,
  rubrik TEXT,
  text TEXT,
  datum TEXT,
  status TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  );
''',
'''
CREATE INDEX IF NOT EXISTS utskick_kodstugor_id ON utskick(kodstugor_id);
''',
'''
CREATE TABLE IF NOT EXISTS volontarer (
  id INTEGER PRIMARY KEY,
  kodstugor_id INT,
  epost TEXT  UNIQUE,
  namn TEXT,
  telefon TEXT,
  password TEXT,
  session TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  );
''',
'''
CREATE INDEX IF NOT EXISTS volontarer_session ON volontarer(session);
''',
'''
CREATE TABLE IF NOT EXISTS volontarer_plannering (
  id INTEGER PRIMARY KEY,
  datum TEXT,
  volontarer_id INT,
  status TEXT,
  kodstugor_id INT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id),
  FOREIGN KEY(volontarer_id) REFERENCES volontarer(id)
  );
''',
'''
CREATE INDEX IF NOT EXISTS volontärer_plannering_kodstugor_id ON volontarer_plannering(kodstugor_id);
''']
