#!/usr/bin/env python
# -*- coding: utf-8 -*-

tables = ['''
  CREATE TABLE IF NOT EXISTS kodstugor (
  id INTEGER PRIMARY KEY,
  namn TEXT,
  sms_text TEXT,
  epost_text TEXT,
  epost_rubrik TEXT,
  epost_text_ja TEXT,
  epost_rubrik_ja TEXT,
  open TEXT
   );
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
  datum INTEGER,
  status TEXT,
  frannummer TEXT,
  skonto TEXT,
  slosen TEXT,
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
CREATE TABLE IF NOT EXISTS deltagande_närvaro (
  id INTEGER PRIMARY KEY,
  deltagare_id INT,
  status TEXT,
  datum TEXT,
  skapad INT,
  FOREIGN KEY(deltagare_id) REFERENCES deltagare(id)
  );
''',
'''
CREATE TABLE IF NOT EXISTS klick_svar (
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
  datum INT,
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
  epost TEXT UNIQUE,
  namn TEXT,
  telefon TEXT,
  utdrag_datum INT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  );
''',
'''
CREATE TABLE IF NOT EXISTS volontarer_roller (
  id INTEGER PRIMARY KEY,
  volontarer_id INT,
  kodstugor_id INT,
  roll TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id),
  FOREIGN KEY(volontarer_id) REFERENCES volontarer(id)
  );
''',
'''
CREATE TABLE IF NOT EXISTS volontarer_plannering (
  id INTEGER PRIMARY KEY,
  datum TEXT,
  volontarer_id INT,
  kodstugor_id INT,
  status TEXT,
  kommentar TEXT,
  FOREIGN KEY(volontarer_id) REFERENCES volontarer(id),
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  );
''',
'''
CREATE TABLE IF NOT EXISTS auth (
  session_id PRIMARY KEY,
  user_data TEXT,
  vailid INT
  );
''',
'''
CREATE TABLE IF NOT EXISTS keyvalue (
  id TEXT UNIQUE PRIMARY KEY,
  text TEXT
  );
''',
'''
INSERT OR IGNORE INTO keyvalue(id, text) VALUES("Intresse anmälan", "")
''',
'''
INSERT OR IGNORE INTO keyvalue(id, text) VALUES("Erbjudande om plats", "")
''',
'''
INSERT OR IGNORE INTO keyvalue(id, text) VALUES("Info Vid Ansökan", "")
''',
'''
INSERT OR IGNORE INTO keyvalue(id, text) VALUES("BESK-konto aktiverat", "")
''',
'''
CREATE TABLE IF NOT EXISTS mail_queue (
  id TEXT UNIQUE PRIMARY KEY,
  date TEXT,
  till TEXT,
  subject TEXT,
  message TEXT,
  status TEXT
  );
''',
'''
CREATE INDEX IF NOT EXISTS mail_queue_status ON mail_queue(status, date);
''',
'''
CREATE TABLE IF NOT EXISTS sms_queue (
  id TEXT UNIQUE PRIMARY KEY,
  date TEXT,
  till TEXT,
  message TEXT,
  status TEXT,
  sms_id TEXT
  );
''',
'''
CREATE INDEX IF NOT EXISTS sms_queue_status ON sms_queue(status, date);
'''
]
