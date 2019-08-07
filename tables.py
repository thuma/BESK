# -*- coding: utf-8 -*-

tables = ['''
  CREATE TABLE IF NOT EXISTS kodstugor (
  id INT PRIMARY KEY,
  namn TEXT,
  sms_text TEXT,
  epost_text TEXT,
  epost_rubrik TEXT ) WITHOUT ROWID;
''',
'''
CREATE TABLE IF NOT EXISTS kodstugor_datum (
  id INT PRIMARY KEY,
  kodstugor_id INT INDEX,
  datum TEXT,
  typ TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  ) WITHOUT ROWID; 
''',
'''
CREATE TABLE IF NOT EXISTS deltagare (
  id INT PRIMARY KEY,
  kodstugor_id INT,
  fornamn TEXT,
  efternamn TEXT,
  kon TEXT,
  foto TEXT,
  framnummer TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  ) WITHOUT ROWID; 
''',
'''
CREATE TABLE IF NOT EXISTS kontaktpersoner (
  id INT PRIMARY KEY,
  fornamn TEXT,
  efternamn TEXT,
  epost TEXT UNIQUE,
  telefon TEXT) WITHOUT ROWID;
''',
'''
CREATE TABLE IF NOT EXISTS kontaktpersoner_deltagare (
  id INT PRIMARY KEY,
  kodstugor_id INT,
  kontaktpersoner_id INT,
  deltagare_id INT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id),
  FOREIGN KEY(kontaktpersoner_id) REFERENCES kontaktpersoner(id),
  FOREIGN KEY(deltagare_id) REFERENCES deltagare(id)
  ) WITHOUT ROWID; 
''',
'''
CREATE TABLE IF NOT EXISTS deltagande (
  id INT PRIMARY KEY,
  kodstugor_id INT,
  deltagare_id INT,
  status TEXT,
  datum TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id),
  FOREIGN KEY(deltagare_id) REFERENCES deltagare(id)
  ) WITHOUT ROWID; 
''',
'''
CREATE TABLE IF NOT EXISTS kick_svar (
  id INT PRIMARY KEY,
  deltagare_id INT,
  svar TEXT,
  datum TEXT
  FOREIGN KEY(deltagare_id) REFERENCES deltagare(id)
  ) WITHOUT ROWID; 
''',
'''
CREATE TABLE IF NOT EXISTS sms_svar (
  id TEXT PRIMARY KEY,
  fran TEXT,
  till TEXT,
  text TEXT,
  datum TEXT) WITHOUT ROWID; 
''',
'''
CREATE TABLE IF NOT EXISTS utskick (
  id INT PRIMARY KEY,
  kodstugor_id INT INDEX,
  typ TEXT,
  rubrik TEXT,
  text TEXT,
  datum TEXT,
  status TEXT,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  ) WITHOUT ROWID;
''',
'''
CREATE TABLE IF NOT EXISTS volontarer (
  id INT PRIMARY KEY,
  kodstugor_id INT,
  epost TEXT UNIQUE,
  namn TEXT,
  telefon TEXT,
  password TEXT,
  session TEXT INDEX,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id)
  ) WITHOUT ROWID;
''',
'''
CREATE TABLE IF NOT EXISTS volontärer_plannering (
  id INT PRIMARY KEY,
  datum TEXT,
  volontarer_id INT,
  status TEXT,
  kodstugor_id INT INDEX,
  FOREIGN KEY(kodstugor_id) REFERENCES kodstugor(id),
  FOREIGN KEY(volontarer_id) REFERENCES volontarer(id),
  ) WITHOUT ROWID;
''']