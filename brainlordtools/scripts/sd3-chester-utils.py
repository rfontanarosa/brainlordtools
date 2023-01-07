__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, sqlite3

resources_path = '../resources/sd3'
dump_path = os.path.join(resources_path, 'dump')
db = os.path.join(resources_path, 'db/sd3.db')
user_name = 'clomax'

fullpath = os.path.join(dump_path, 'sd3.txt')
fullpathIta = os.path.join(dump_path, 'sd3-ita.txt')
fullpathMagno = os.path.join(dump_path, 'sd3-magno.txt')
"""
fullpath = os.path.join(dump_path, 'sd3OLD.txt')
fullpathIta = os.path.join(dump_path, 'sd3OLD-ita.txt')
"""

def convertToMagno(text):
	#
	text = text.replace('\n', '<JUMP>\n')
	#
	text = text.replace('<END><JUMP>\n<END>', '<END><END>')
	text = text.replace('<END><JUMP>\n<OPEN>', '<END><OPEN>\n')
	text = text.replace('<BOX><OPEN>', '<58><OPEN>\n')
	text = text.replace('<BOX><PAGE><JUMP>\n', '<58><PAUSE>\n')
	text = text.replace('<LINE><OPEN>', '<5E><OPEN>\n')
	#
	text = text.replace('<CHAR 0>', '<19><00>')
	text = text.replace('<CHAR 1>', '<19><01>')
	text = text.replace('<CHAR 2>', '<19><02>')
	text = text.replace('<CHAR 3>', '<19><03>')
	#
	text = text.replace('<WHITE>', '<+B.>')
	text = text.replace('<YELLOW>', '<+J.>')
	text = text.replace('<MONO WHITE>', '<+B_>')
	text = text.replace('<MONO YELLOW>', '<+J_>')
	text = text.replace('<MONO NARROW WHITE>', '<+b_>')
	#
	text = text.replace('<DURAN>', '<19><F8><00>')
	text = text.replace('<KEVIN>', '<19><F8><01>')
	text = text.replace('<HAWK>', '<19><F8><02>')
	text = text.replace('<ANGELA>', '<19><F8><03>')
	text = text.replace('<CARLIE>', '<19><F8><04>')
	text = text.replace('<LISE>', '<19><F8><05>')
	#
	text = text.replace('<PAD 1>', '<TAB 01>')
	text = text.replace('<PAD 2>', '<TAB 02>')
	text = text.replace('<PAD 3>', '<TAB 03>')
	text = text.replace('<PAD 4>', '<TAB 04>')
	text = text.replace('<PAD 5>', '<TAB 05>')
	text = text.replace('<PAD 6>', '<TAB 06>')
	text = text.replace('<PAD 7>', '<TAB 07>')
	text = text.replace('<PAD 8>', '<TAB 08>')
	text = text.replace('<PAD 9>', '<TAB 09>')
	text = text.replace('<PAD 10>', '<TAB 0A>')
	text = text.replace('<PAD 11>', '<TAB 0B>')
	text = text.replace('<PAD 12>', '<TAB 0C>')
	text = text.replace('<PAD 13>', '<TAB 0D>')
	text = text.replace('<PAD 14>', '<TAB 0E>')
	text = text.replace('<PAD 15>', '<TAB 0F>')
	text = text.replace('<PAD 15>', '<TAB 1C>')
	text = text.replace('<PAD 26>', '<TAB 1A>')
	#
	text = text.replace('<ALT>', '<7B>')
	text = text.replace('<F1>', '<F1>\n')
	text = text.replace('<ITEM 500>', '<1B><F5><00>')
	text = text.replace('<ITEM 501>', '<1B><F5><01>')
	text = text.replace('<ITEM 502>', '<1B><F5><02>')
	text = text.replace('<ITEM 503>', '<1B><F5><03>')
	text = text.replace('<ITEM 50B>', '<1B><F5><0B>')
	text = text.replace('<ITEM 509>', '<1B><F5><09>')
	#
	text = text.replace('<OR>', '<14>')
	text = text.replace('<BOX>', '<58>\n')
	text = text.replace('<LINE>', '<5E>')
	text = text.replace('<PAGE><JUMP>', '<PAUSE>')
	text = text.replace('<END><JUMP>', '<END>')
	return text

conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
with open(fullpath, 'rb') as f:
	id = 1
	block = 0
	id2 = ''
	text_encoded = ''
	for line in f:
		if line == '\n':
			text_length = len(text_encoded)
			#block = id2.partition(':')[2]
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?, ?)', (id, '', text_encoded, '', '', text_length, block, id2))
			id += 1
			text_encoded = ''
		else:
			if text_encoded == '' and '[Block $' in line:
				id2 = line.strip('\n')
			else:
				text_encoded += line
			"""
			if text_encoded == '' and '[Sentence $' in line :
				id2 = line.strip('[Sentence $')
				id2 = id2.strip(']\n')
			else:
				if '[/Sentence]' not in line:
					text_encoded += line
			"""
cur.close()
conn.commit()
conn.close()

if os.path.isfile(fullpathIta):
	os.remove(fullpathIta)
if os.path.isfile(fullpathMagno):
	os.remove(fullpathMagno)

conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
with open(fullpathIta, 'ab') as f1, open(fullpathMagno, 'ab') as f2:
	cur.execute("SELECT text, new_text, text_encoded, id, new_text2, id2 FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text ORDER BY t1.id" % user_name)
	for row in cur:
		id2 = row[5]
		id = row[3]
		original_text = row[2]
		new_text = row[4]
		text = new_text if new_text else original_text
		f1.write(id2 + '\n')
		f1.write(text)
		f1.write('\n')
		"""
		f.write('[Sentence $%s]\n' % (id2))
		f.write(text)
		f.write('[/Sentence]\n\n')
		"""
		text = convertToMagno(text)
		f2.write(id2 + '\n')
		f2.write(text)
		f2.write('\n')
cur.close()
conn.commit()
conn.close()

"""
import urllib
images = ["32.gif", "33.gif", "39.gif", "40.gif", "41.gif", "44.gif", "45.gif", "46.gif", "48.gif", "49.gif", "50.gif", "51.gif", "52.gif", "53.gif", "54.gif", "55.gif", "56.gif", "57.gif", "58.gif", "63.gif", "65.gif", "66.gif", "67.gif", "68.gif", "69.gif", "70.gif", "71.gif", "72.gif", "73.gif", "74.gif", "75.gif", "76.gif", "77.gif", "78.gif", "79.gif", "80.gif", "81.gif", "82.gif", "83.gif", "84.gif",       "85.gif", "86.gif", "87.gif", "88.gif", "89.gif", "90.gif", "97.gif", "98.gif", "99.gif", "100.gif", "101.gif", "102.gif", "103.gif", "104.gif", "105.gif", "106.gif", "107.gif", "108.gif", "109.gif", "110.gif", "111.gif", "112.gif", "113.gif", "114.gif", "115.gif", "116.gif", "117.gif", "118.gif", "119.gif", "120.gif", "121.gif", "122.gif", "196.gif","214.gif", "220.gif", "223.gif", "228.gif", "246.gif", "252.gif", "bg0.png", "bg1.png", "bg2.png", "bg3.png", "bg4.png", "bg5.png", "bgx.png", "bgz.png", "window.png", "back.gif", "next.gif"]
for image in images:
	urllib.urlretrieve('http://www.secretofmana2.de/text-tool/images/' + image, 'sd3/' + image)
"""
