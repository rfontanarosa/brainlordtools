## -*- coding: latin-1 -*-

__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, re, time, sqlite3
from collections import OrderedDict

resources_path = '../resources/sd3'
dump_path = os.path.join(resources_path, 'magno')
translation_path = os.path.join(resources_path, 'translation-magno')
import_path = os.path.join('/Users/rfontanarosa/git/brainlordresources/sd3/Italian/')
fileNames = ('Bank0_ita.txt', 'Bank1_ita.txt', 'Bank2_ita.txt', 'Items_ita.txt')

db = os.path.join(resources_path, 'db/sd3-magno.db')
db2 = os.path.join(resources_path, '/Users/rfontanarosa/git/brainlordtools/resources/db/sd3-magno.db')
user_name = 'clomax'

if True:
	""" IMPORT DUMP """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	id = 1
	for block, fileName in enumerate(fileNames):
		filePath = os.path.join(dump_path, fileName)
		with open(filePath, 'rb') as f:
			#
			buffer = OrderedDict()
			for line in f:
				if '<INI ' in line:
					inis = re.findall('[^>]+>', line)
					for ini in inis:
						id2 = ini.strip('<INI ').strip('>')
						buffer[id2] = ''
				else:
					last = buffer.keys()[-1]
					buffer[last] += line
			#
			for id2, text in buffer.items():
				text_length = len(text)
				text_encoded = text.strip('\n\r')
				text_encoded = text_encoded.decode("iso-8859-1").encode("utf-8")
				cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?, ?)', (id, '', text_encoded, '', '', text_length, block, id2))
				id += 1
	cur.close()
	conn.commit()
	conn.close()

if True:
	""" IMPORT TRANSLATION """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	id = 1
	for block, fileName in enumerate(fileNames):
		filePath = os.path.join(import_path, fileName)
		with open(filePath, 'rb') as f:
			#
			buffer = OrderedDict()
			for line in f:
				if '<INI ' in line:
					inis = re.findall('[^>]+>', line)
					for ini in inis:
						id2 = ini.strip('<INI ').strip('>')
						buffer[id2] = ''
				else:
					last = buffer.keys()[-1]
					buffer[last] += line
			#
			for id2, text in buffer.items():
				text_length = len(text)
				text = text.strip('\n\r')
				text = text.decode("iso-8859-1").encode("utf-8")
				cur.execute('insert or replace into trans values (?, ?, ?, ?, ?, ?, ?)', (id, 'clomax', text, '', 2, time.time(), ''))
				id += 1
	cur.close()
	conn.commit()
	conn.close()

if True:
	""" EXPORT """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	for block, fileName in enumerate(fileNames):
		filePath = os.path.join(translation_path, fileName)
		with open(filePath, 'w') as f:
			cur.execute("SELECT id2, text_encoded, new_text FROM texts AS t1 LEFT JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE block=%d ORDER BY t1.id" % (user_name, block))
			for row in cur:
				id2 = row[0]
				original_text = row[1]
				new_text = row[2]
				ini = '<INI ' + id2 + '>'
				text = new_text if new_text else original_text
				if text == '':
					f.write(ini)
				else:
					f.write(ini + '\r\n')
					text = text.decode("utf-8").encode("iso-8859-1")
					f.write(text + '\r\n\r\n')
	cur.close()
	conn.commit()
	conn.close()
