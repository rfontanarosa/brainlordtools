__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sqlite3
from enum import IntEnum
from typing import NamedTuple

class TranslationStatus(IntEnum):
    UNDONE = 0
    PARTIALLY = 1
    DONE = 2

class TranslationRecord(NamedTuple):
    id: int
    text: str
    text_decoded: str
    address: str
    pointer_addresses: str
    translation: str
    author: str
    ref: str
    date: str

def insert_text(cur, id, text, decoded_text, address, pointer_adresses, block, ref) -> None:
    cur.execute('INSERT OR REPLACE INTO texts VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (id, sqlite3.Binary(text), decoded_text, address, pointer_adresses, len(text), str(block), ref))

def insert_translation(cur, id_text, project, author, translation, status, date, tags, comment) -> None:
    cur.execute('INSERT OR REPLACE INTO translations VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (id_text, project, author, translation, status, date, tags, comment))

def update_translation(cur, id_text, project, author, translation, status, date, tags, comment) -> None:
    cur.execute('UPDATE translations SET translation=?, status=?, date=?, tags=?, comment=? WHERE id_text=? AND project=? AND author=?', (translation, status, date, tags, comment, id_text, project, author))

def select_texts(cur, blocks=None):
    query = f"SELECT t1.id, t1.text_decoded FROM texts AS t1"
    if blocks:
        query += " WHERE t1.block IN ({})".format(', '.join(blocks))
    query += " ORDER BY t1.id"
    return cur.execute(query)

def select_translation_by_author(cur, author, blocks=None) -> TranslationRecord:
    query = f"SELECT t1.id, t1.text, t1.text_decoded, t1.address, t1.pointer_addresses, t2.translation, t2.author, t1.ref, t2.date FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM translations WHERE author='{author}' AND status = 2) AS t2 ON t1.id=t2.id_text"
    if blocks:
        query += " WHERE t1.block IN ({})".format(', '.join(blocks))
    query += " ORDER BY t1.id"
    return cur.execute(query)

def select_most_recent_translation(cur, blocks=None) -> TranslationRecord:
    query = "SELECT * FROM (SELECT t1.id, t1.text, t1.text_decoded, t1.address, t1.pointer_addresses, t2.translation, t2.author, t1.ref, COALESCE(t2.date, 1) AS date FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM translations WHERE status = 2) AS t2 ON t1.id=t2.id_text) WHERE 1=1 GROUP BY id HAVING MAX(date)"
    if blocks:
        query = "SELECT * FROM (SELECT t1.id, t1.text, t1.text_decoded, t1.address, t1.pointer_addresses, t2.translation, t2.author, t1.ref, COALESCE(t2.date, 1) AS date FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM translations WHERE status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block IN ({})) WHERE 1=1 GROUP BY id HAVING MAX(date)".format(', '.join(blocks))
    query += " ORDER BY id"
    return cur.execute(query)
