__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, sqlite3, time
from collections import OrderedDict

user_name = 'clomax'

resources_path = '../../brainlordresources/ffmq'
dump_path = os.path.join(resources_path, 'dump')
translation_path = os.path.join(resources_path, 'translation')
user_path = os.path.join(resources_path, user_name)
db = os.path.join(resources_path, 'db/ffmq.db')

dialogues_path = os.path.join(dump_path, 'dump_eng.txt')
dialogues_ita_path = os.path.join(translation_path, 'dump_ita.txt')
dialogues_user_path = os.path.join(user_path, 'dump_ita.txt')

import_dump= True
export_user_translation = True
import_user_translation = False

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dialogues_path, 'rb') as f:
    block = 1
    id = 0
    buffer = OrderedDict()
    for line in f:
      if '[BLOCK ' in line:
        id += 1
        buffer[id] = ['', line]
      else:
        buffer[id][0] += line
    for id, value in buffer.items():
      [text, id2] = value
      text_length = len(text)
      text_encoded = text.strip('\n\r')
      #text_encoded = text_encoded.decode("iso-8859-1").encode("utf-8")
      cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?, ?)', (id, '', text_encoded, '', '', text_length, block, id2))
  cur.close()
  conn.commit()
  conn.close()

if export_user_translation:
  if os.path.isfile(dialogues_user_path):
    os.remove(dialogues_user_path)
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dialogues_user_path, 'ab') as f:
    cur.execute("SELECT text, new_text, text_encoded, id, id2 FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = 1 ORDER BY t1.id" % user_name)
    for row in cur:
      id2 = row[4]
      original_text = row[2]
      new_text = row[1]
      text = new_text if new_text else original_text
      f.write(id2)
      f.write(text)
      f.write('\r\n')
      f.write('\r\n')
  cur.close()
  conn.commit()
  conn.close()

"""
if import_user_translation:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  id = 1
  date = time.time()
  with open(dialoguesUserPath, 'rb') as f:
    for line in f:
      splittedLine = line.split('\t')
      id2 = splittedLine[0].replace('{', '').replace('}', '').decode('utf-8-sig')
      if user_name == 'lorenzooone':
        line1 = next(f)
        splittedLine = line1.split('\t')
        id2 = splittedLine[0].replace('{', '').replace('}', '').replace('I:', '')
      if len(splittedLine) == 2:
        text = splittedLine[1].replace('\r', '').replace('\n', '')
        id = int(id2) + 1
        text1 = text
        cur.execute('insert or replace into trans values (?, ?, ?, ?, ?, ?, ?)', (id, user_name, text, text1, 2, date, ''))
      id += 1
  cur.close()
  conn.commit()
  conn.close()
"""
