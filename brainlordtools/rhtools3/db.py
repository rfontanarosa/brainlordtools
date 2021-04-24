import sys, sqlite3

def insert_text(cur, id, text, decoded_text, address, pointer_adresses, block, ref):
    cur.execute('INSERT OR REPLACE INTO texts VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (id, text, decoded_text, address, pointer_adresses, len(text), block, ref))

def insert_translation(cur, id_text, project, author, translation, status, date, tags, comment):
    cur.execute('INSERT OR REPLACE INTO translations VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (id_text, project, author, translation, status, date, tags, comment))

def update_translation(cur, id_text, project, author, translation, status, date, tags, comment):
    cur.execute('UPDATE translations SET translation=?, status=?, date=?, tags=?, comment=? WHERE id_text=? AND project=? AND author=?', (translation, status, date, tags, comment, id_text, project, author))

def select_translation_by_author(cur, author, blocks):
    blocks = ", ".join(blocks)
    return cur.execute("SELECT t1.id, t1.text, t1.text_decoded, t1.address, t1.pointer_addresses, t2.translation, t1.ref FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM translations WHERE author='{}' AND status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block IN ({})".format(author, blocks))

def select_most_recent_translation(cur, blocks):
    blocks = ", ".join(blocks)
    return cur.execute("SELECT * FROM (SELECT t1.id, t1.text, t1.text_decoded, t1.address, t1.pointer_addresses, t2.translation, t2.author, COALESCE(t2.date, 1) AS date, t1.ref FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM translations WHERE status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block IN ({})) WHERE 1=1 GROUP BY id HAVING MAX(date)".format(blocks))

def convert_to_binary(text):
    return sqlite3.Binary(text)
