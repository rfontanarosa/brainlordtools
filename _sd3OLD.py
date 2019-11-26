__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3
from collections import OrderedDict

db = '. /resources/sd3/db/sd3.db'
dump_path = './resources/sd3/dump/'
user_name = 'clomax'

fullpath = os.path.join(dump_path, 'sd3OLD.txt')
fullpathIta = os.path.join(dump_path, 'sd3OLD-ita.txt')

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
			if text_encoded == '' and '[Sentence $' in line :
				id2 = line.strip('[Sentence $')
				id2 = id2.strip(']\n')
			else:
				if '[/Sentence]' not in line:
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
		f.write('[Sentence $%s]\n' % (id2))
		f.write(text)
		f.write('[/Sentence]\n\n')
cur.close()
conn.commit()
conn.close()

"""
import urllib
images = ["32.gif", "33.gif", "39.gif", "40.gif", "41.gif", "44.gif", "45.gif", "46.gif", "48.gif", "49.gif", "50.gif", "51.gif", "52.gif", "53.gif", "54.gif", "55.gif", "56.gif", "57.gif", "58.gif", "63.gif", "65.gif", "66.gif", "67.gif", "68.gif", "69.gif", "70.gif", "71.gif", "72.gif", "73.gif", "74.gif", "75.gif", "76.gif", "77.gif", "78.gif", "79.gif", "80.gif", "81.gif", "82.gif", "83.gif", "84.gif",       "85.gif", "86.gif", "87.gif", "88.gif", "89.gif", "90.gif", "97.gif", "98.gif", "99.gif", "100.gif", "101.gif", "102.gif", "103.gif", "104.gif", "105.gif", "106.gif", "107.gif", "108.gif", "109.gif", "110.gif", "111.gif", "112.gif", "113.gif", "114.gif", "115.gif", "116.gif", "117.gif", "118.gif", "119.gif", "120.gif", "121.gif", "122.gif", "196.gif","214.gif", "220.gif", "223.gif", "228.gif", "246.gif", "252.gif", "bg0.png", "bg1.png", "bg2.png", "bg3.png", "bg4.png", "bg5.png", "bgx.png", "bgz.png", "window.png", "back.gif", "next.gif"]
for image in images:
	urllib.urlretrieve('http://www.secretofmana2.de/text-tool/images/' + image, 'sd3/' + image)
"""
