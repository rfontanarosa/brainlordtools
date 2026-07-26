__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

from enum import IntEnum
from typing import NamedTuple

class TranslationStatus(IntEnum):
    UNDONE = 0
    PARTIALLY = 1
    DONE = 2

class TranslationRecord(NamedTuple):
    id: int
    text: str
    address: str
    pointer_addresses: str
    translation: str
    author: str
    ref: str
    date: str

def insert_text(cur, id, text, address, pointer_addresses, size, block, ref, dump_type, filename, file_index) -> None:
    cur.execute(
        'INSERT OR REPLACE INTO texts (id, text, address, pointer_addresses, size, block, ref, dump_type, filename, file_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (id, text, address, pointer_addresses, size, str(block), ref, dump_type, filename, file_index)
    )

def insert_translation(cur, filename, file_index, author, translation, status, date, tags, comment) -> None:
    query = '''
    INSERT INTO translations (filename, file_index, author, translation, status, date, tags, comment)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(filename, file_index, author) DO UPDATE SET
        translation = excluded.translation,
        status = excluded.status,
        date = COALESCE(translations.date, excluded.date),
        tags = excluded.tags,
        comment = excluded.comment
    '''
    cur.execute(query, (filename, file_index, author, translation, status, date, tags, comment))

def update_translation(cur, filename, file_index, author, translation, status, date, tags, comment) -> None:
    cur.execute('UPDATE translations SET translation=?, status=?, date=?, tags=?, comment=? WHERE filename=? AND file_index=? AND author=?', (translation, status, date, tags, comment, filename, file_index, author))

def select_texts(cur, blocks=None):
    query = "SELECT t1.id, t1.text FROM texts AS t1"
    if blocks:
        query += " WHERE t1.block IN ({})".format(', '.join(blocks))
    query += " ORDER BY t1.id"
    return cur.execute(query)

def select_text_file_locations(cur):
    return cur.execute("SELECT id, filename, file_index FROM texts")

def select_translation_by_author(cur, author, blocks=None) -> TranslationRecord:
    query = f"SELECT t1.id, NULL, t1.text, t1.address, t1.pointer_addresses, t2.translation, t2.author, t1.ref, t2.date FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM translations WHERE author='{author}' AND status = 2) AS t2 ON t1.filename=t2.filename AND t1.file_index=t2.file_index"
    if blocks:
        query += " WHERE t1.block IN ({})".format(', '.join(blocks))
    query += " ORDER BY t1.id"
    return cur.execute(query)

def select_most_recent_translation(cur, blocks=None) -> TranslationRecord:
    query = "SELECT * FROM (SELECT t1.id, NULL, t1.text, t1.address, t1.pointer_addresses, t2.translation, t2.author, t1.ref, COALESCE(t2.date, 1) AS date FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM translations WHERE status = 2) AS t2 ON t1.filename=t2.filename AND t1.file_index=t2.file_index) WHERE 1=1 GROUP BY id HAVING MAX(date)"
    if blocks:
        query = "SELECT * FROM (SELECT t1.id, NULL, t1.text, t1.address, t1.pointer_addresses, t2.translation, t2.author, t1.ref, COALESCE(t2.date, 1) AS date FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM translations WHERE status = 2) AS t2 ON t1.filename=t2.filename AND t1.file_index=t2.file_index WHERE t1.block IN ({})) WHERE 1=1 GROUP BY id HAVING MAX(date)".format(', '.join(blocks))
    query += " ORDER BY id"
    return cur.execute(query)
