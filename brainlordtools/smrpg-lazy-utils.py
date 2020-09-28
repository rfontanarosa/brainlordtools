__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, sqlite3, time

userName = 'ombra'

resources_path = '../../brainlordresources/smrpg'
dump_path = os.path.join(resources_path, 'dump')
translation_path = os.path.join(resources_path, 'translation')
user_path = os.path.join(resources_path, userName)
db = os.path.join(resources_path, 'db/smrpg.db')

dialoguesPath = os.path.join(dump_path, 'dialogues.txt')
dialoguesItaPath = os.path.join(translation_path, 'dialogues-ita.txt')
dialoguesUserPath = os.path.join(user_path, 'dialogues.txt')

battleDialoguesPath = os.path.join(dump_path, 'battleDialogues.txt')
battleDialoguesItaPath = os.path.join(translation_path, 'battleDialogues-ita.txt')
battleDialoguesUserPath = os.path.join(user_path, 'battleDialogues.txt')

importAll = False
exportTranslationByUser = False
importTranslationByUser = True

if importAll:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  id = 1
  with open(dialoguesPath, 'rb') as f:
    for line in f:
      splittedLine = line.split('\t')
      id2 = splittedLine[0].replace('{', '').replace('}', '')
      text = splittedLine[1].replace('\r', '').replace('\n', '')
      cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?, ?)', (id, '', text, '', '', 0, 1, id2))
      id += 1
  with open(battleDialoguesPath, 'rb') as f:
    for line in f:
      splittedLine = line.split('\t')
      id2 = splittedLine[0].replace('{', '').replace('}', '')
      text = splittedLine[1].replace('\r', '').replace('\n', '')
      cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?, ?)', (id, '', text, '', '', 0, 2, id2))
      id += 1
  cur.close()
  conn.commit()
  conn.close()

if exportTranslationByUser:
  if os.path.isfile(dialoguesItaPath):
    os.remove(dialoguesItaPath)
  if os.path.isfile(battleDialoguesItaPath):
    os.remove(battleDialoguesItaPath)
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dialoguesItaPath, 'ab') as f:
    cur.execute("SELECT text, new_text, text_encoded, id, id2 FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = 1 ORDER BY t1.id" % userName)
    for row in cur:
      id = row[3]
      original_text = row[2]
      new_text = row[2]
      text = new_text if new_text else original_text
      f.write('{' + str(id).zfill(4) + '}' + '\t' + text)
      f.write('\n')
  with open(battleDialoguesItaPath, 'ab') as f:
    cur.execute("SELECT text, new_text, text_encoded, id, id2 FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = 2 ORDER BY t1.id" % userName)
    for row in cur:
      id = row[3]
      original_text = row[2]
      new_text = row[2]
      text = new_text if new_text else original_text
      f.write('{' + str(id).zfill(4) + '}' + '\t' + text)
      f.write('\r\n')
  cur.close()
  conn.commit()
  conn.close()

if importTranslationByUser:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  id = 1
  date = time.time()
  with open(dialoguesUserPath, 'rb') as f:
    for line in f:
      splittedLine = line.split('\t')
      id2 = splittedLine[0].replace('{', '').replace('}', '').decode('utf-8-sig')
      if userName == 'lorenzooone':
        line1 = next(f)
        splittedLine = line1.split('\t')
        id2 = splittedLine[0].replace('{', '').replace('}', '').replace('I:', '')
      if len(splittedLine) == 2:
        text = splittedLine[1].replace('\r', '').replace('\n', '')
        id = int(id2) + 1
        text1 = text
        cur.execute('insert or replace into trans values (?, ?, ?, ?, ?, ?, ?)', (id, userName, text, text1, 2, date, ''))
      id += 1
  with open(battleDialoguesUserPath, 'rb') as f:
    for line in f:
      splittedLine = line.split('\t')
      id2 = splittedLine[0].replace('{', '').replace('}', '').decode('utf-8-sig')
      if userName == 'lorenzooone':
        line1 = next(f)
        splittedLine = line1.split('\t')
        id2 = splittedLine[0].replace('{', '').replace('}', '').replace('I:', '')
      if len(splittedLine) == 2:
        text = splittedLine[1].replace('\r', '').replace('\n', '')
        id = int(id2) + 4097
        text1 = text
        cur.execute('insert or replace into trans values (?, ?, ?, ?, ?, ?, ?)', (id, userName, text, text1, 2, date, ''))
      id += 1
  cur.close()
  conn.commit()
  conn.close()
