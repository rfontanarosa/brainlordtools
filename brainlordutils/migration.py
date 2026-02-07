import sys, sqlite3

# GAME = 'brainlord'
# GAME = 'neugier'
# GAME = 'ffmq'
# GAME = 'smrpg'
# GAME = 'bof'
# GAME = 'brandish'
GAME = 'sd3'

# sqlite3 /Users/robertofontanarosa/git/brainlordresources/GAME/db/GAME.sqlite3 < /Users/robertofontanarosa/git/brainlordtools/db.sql
db_path = f'/Users/robertofontanarosa/git/brainlordresources/{GAME}/db/'
old_db_name = f'{GAME}.db'
new_db_name = f'{GAME}.sqlite3'

if True:

    print(db_path + old_db_name)
    old_conn = sqlite3.connect(db_path + old_db_name)
    old_conn.text_factory = str
    old_cur = old_conn.cursor()
    new_conn = sqlite3.connect(db_path + new_db_name)
    new_conn.text_factory = str
    new_cur = new_conn.cursor()

    old_cur.execute('SELECT * FROM trans')
    for row in old_cur:
        id_text = row[0]
        author = row[1]
        new_text = row[2]
        if GAME == 'neugier':
            new_text = new_text.replace('{08}', '…')
            new_text = new_text.replace('{47}', 'ō')
            new_text = new_text.replace('{8b}', '~')
            new_text = new_text.replace('{28}', '‘')
            new_text = new_text.replace('{0e}', '”')
            new_text = new_text.replace('{6f}', '“')
            new_text = new_text[:-4]
        elif GAME == 'bof':
            new_text = new_text.replace('{01}', '')
        elif GAME == 'brandish':
            new_text = new_text.replace('{7C}', 'à')
            new_text = new_text.replace('{5B}', 'è')
            new_text = new_text.replace('{5C}', 'é')
            new_text = new_text.replace('{5D}', 'ì')
            new_text = new_text.replace('{5E}', 'ò')
            new_text = new_text.replace('{5F}', 'ù')
            new_text = new_text.replace('{60}', 'È')
        new_text2 = row[3]
        status = row[4]
        date = row[5]
        comment = row[6]
        new_cur.execute('INSERT OR REPLACE INTO translations VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (id_text, 'TEST', author, new_text, status, date, '', comment))

    new_cur.close()
    new_conn.commit()
    new_conn.close()
    old_cur.close()
    old_conn.commit()
    old_conn.close()
