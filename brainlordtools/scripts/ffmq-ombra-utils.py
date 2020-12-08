__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, sqlite3
from collections import OrderedDict

user_name = 'clomax'
resources_path = '../../../brainlordresources/ffmq'

db = os.path.join(resources_path, 'db/ffmq.db')
dump_path = os.path.join(resources_path, 'dump')
translation_path = os.path.join(resources_path, 'translation')
user_path = os.path.join(resources_path, user_name)
dump_fullpath = os.path.join(dump_path, 'dump_eng.txt')
dump_ita_fullpath = os.path.join(translation_path, 'dump_ita.txt')
dump_user_fullpath = os.path.join(translation_path, 'dump_ita_{}.txt'.format(user_name))

import_dump= True
export_user_translation = True

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_fullpath, 'r') as f:
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
      cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?, ?)', (id, '', text_encoded, '', '', text_length, block, id2))
  cur.close()
  conn.commit()
  conn.close()

if export_user_translation:
  if os.path.isfile(dump_user_fullpath):
    os.remove(dump_user_fullpath)
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_user_fullpath, 'a') as f:
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
