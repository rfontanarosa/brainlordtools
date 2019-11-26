__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3
from collections import OrderedDict

db = './resources/sd3/db/sd3.db'
dump_path = './resources/sd3/dump/'
user_name = 'clomax'

fullpath = os.path.join(dump_path, 'sd3.txt')
fullpathIta = os.path.join(dump_path, 'sd3-ita.txt')

conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
with open(fullpath, 'rb') as f:
	id = 1
	id2 = ''
	text_encoded = ''
	for line in f:
		if line == '\n':
			text_length = len(text_encoded)
			block = id2.partition(':')[2]
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?, ?)', (id, '', text_encoded, '', '', text_length, block, id2))
			id += 1
			text_encoded = ''
		else:
			if text_encoded == '' and '[Block $' in line:
				id2 = line.strip('\n')
			else:
				text_encoded += line
cur.close()
conn.commit()
conn.close()

if os.path.isfile(fullpathIta):
	os.remove(fullpathIta)

conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
with open(fullpathIta, 'ab') as f:
	cur.execute("SELECT text, new_text, text_encoded, id, new_text2, id2 FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text ORDER BY t1.id" % user_name)
	for row in cur:
		id2 = row[5]
		id = row[3]
		original_text = row[2]
		new_text = row[4]
		if new_text:
			text = new_text
		else:
			text = original_text
		f.write(id2 + '\n')
		f.write(text)
		f.write('\n')
cur.close()
conn.commit()
conn.close()
