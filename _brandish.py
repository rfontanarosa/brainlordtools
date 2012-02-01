__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys
import os
import mmap

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit('Missing HexByteConversion module!')

try:
	from Table import Table
	from Dump import Dump
	from utils import *
except ImportError:
	sys.exit('Missing BrandishTools module!')	

CRC32 = '74F70A0B'
	
TEXT_BLOCK_START = 0x50fbe
TEXT_BLOCK_END = 0x594ef
TEXT_BLOCK_LIMIT = 0x594ef
TEXT_BLOCK_SIZE = TEXT_BLOCK_END - TEXT_BLOCK_START
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

TEXT_POINTER_BLOCK_START = 0x50d2a
TEXT_POINTER_BLOCK_END = 0x50fbd

filename = 'roms/Brandish (U) [!].smc'
filename2 = 'roms/Brandish (U) [!] - Copy.smc'
tablename = "tbls/Brandish (U) [!].tbl"
dumpname_txt = 'dump/brandish_dump.txt'
dumpname_xml = 'dump/brandish_dump.xml'
db = '/Program Files/Apache Software Foundation/Apache2.2/htdocs/brandish/db/brandish.db'

table = Table(tablename)

# CHECKSUM (CRC32)
if crc32(filename) != CRC32:
	sys.exit('CHECKSUM: FAIL')
else:
	print 'CHECKSUM: OK'

# DUMP (TXT AND XML USING DUMP.PY)
with open(filename, 'r+b') as f:
	table = Table(tablename)
	map = mmap.mmap(f.fileno(), 0)
	text_extracted = Dump.extract(map, start=TEXT_BLOCK_START, end=TEXT_BLOCK_END)	
	dump = Dump(dump=text_extracted)
	dump.toTxt(table=table, filename="dump/brandish_dump2.txt")
	dump.toXml(table=table, filename="dump/brandish_dump2.xml")
	map.close()

# DUMP (TXT)
with open(filename, "rb+") as f:
	f.seek(TEXT_POINTER_BLOCK_START)
	with open(dumpname_txt, "w") as out:
		while(f.tell() < TEXT_POINTER_BLOCK_END):			
			curr_pointer_address = f.tell()
			curr_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
			next_pointer_address = f.tell()
			if (next_pointer_address < TEXT_POINTER_BLOCK_END):
				next_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
				f.seek(f.tell() - 2)
			else:
				next_pointer_value = None
			with open(filename, "r+b") as f2:
				f2.seek(curr_pointer_value)
				if (next_pointer_value):
					text = f2.read(next_pointer_value - curr_pointer_value)
				else:
					text = ""
					while True:
						b = f2.read(1)
						i = byte2int(b)
						if (i == 255):
							break
						else:
							text += b
				text = table.encode(text, separated_byte_format=True)
				out.write(text)
				
# DUMP (XML)
from xml.dom.minidom import *
with open(filename, "rb") as f:
	doc = Document()
	root = doc.createElement("root")
	root.setAttribute("file", filename)
	root.setAttribute("size", str(TEXT_BLOCK_SIZE))
	id = 1
	f.seek(TEXT_POINTER_BLOCK_START)
	while(f.tell() < TEXT_POINTER_BLOCK_END):
		curr_pointer_address = f.tell()
		curr_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
		next_pointer_address = f.tell()
		if (next_pointer_address < TEXT_POINTER_BLOCK_END):
			next_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
			f.seek(f.tell() - 2)
		else:
			next_pointer_value = None
		with open(filename, 'rb') as f2:
			f2.seek(curr_pointer_value)
			if (next_pointer_value):
				size = next_pointer_value - curr_pointer_value
			else:
				size = TEXT_BLOCK_LIMIT - f2.tell()
			text = f2.read(size)
			text_encoded = table.encode(text, separated_byte_format=True)
			elem = doc.createElement('text')
			elem.setAttribute('id', str(id))
			elem.setAttribute('text_address', int2hex(curr_pointer_value))
			elem.setAttribute('pointer_address', int2hex(int(curr_pointer_address)))
			elem.setAttribute('size', str(size))
			if (next_pointer_value):
				elem.setAttribute("next_pointer_address", int2hex(int(curr_pointer_value) + size))
			cdata = doc.createCDATASection(text_encoded)
			#cdata = doc.createTextNode(text_encoded)
			elem.appendChild(cdata)
			root.appendChild(elem)
			id += 1
	doc.appendChild(root)
	with open(dumpname_xml, 'wb') as out:
		doc.writexml(out, encoding='latin-1')

#DUMP (TXTS)
with open(filename, "rb") as f:
	id = 1
	f.seek(TEXT_POINTER_BLOCK_START)
	while(f.tell() < TEXT_POINTER_BLOCK_END):
		curr_pointer_address = f.tell()
		curr_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
		next_pointer_address = f.tell()
		if (next_pointer_address < TEXT_POINTER_BLOCK_END):
			next_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
			f.seek(f.tell() - 2)
		else:
			next_pointer_value = None
		with open(filename, 'rb') as f2:
			f2.seek(curr_pointer_value)
			if (next_pointer_value):
				size = next_pointer_value - curr_pointer_value
			else:
				size = TEXT_BLOCK_LIMIT - f2.tell()
			text = f2.read(size)
			text_encoded = table.encode(text, separated_byte_format=True)
			pointer_address = int2hex(int(curr_pointer_address))
			with open("dump/" + str(id) + ".txt", "w") as out:
				out.write(text_encoded)
				pass
			id += 1

#DUMP (SQLITE3)
import sqlite3
conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
with open(filename, "rb") as f:
	id = 1
	f.seek(TEXT_POINTER_BLOCK_START)
	while(f.tell() < TEXT_POINTER_BLOCK_END):
		curr_pointer_address = f.tell()
		curr_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
		next_pointer_address = f.tell()
		if (next_pointer_address < TEXT_POINTER_BLOCK_END):
			next_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
			f.seek(f.tell() - 2)
		else:
			next_pointer_value = None
		with open(filename, 'rb') as f2:
			f2.seek(curr_pointer_value)
			if (next_pointer_value):
				size = next_pointer_value - curr_pointer_value
			else:
				size = TEXT_BLOCK_LIMIT - f2.tell()
			text = f2.read(size)
			text_bynary = sqlite3.Binary(text)
			text_encoded = table.encode(text, separated_byte_format=True)
			#text_encoded_binary = sqlite3.Binary(text_encoded)
			text_address = int2hex(curr_pointer_value)
			pointer_address = int2hex(int(curr_pointer_address))
			cur.execute("insert or replace into texts values (?, ?, ?, ?, ?, ?)", (id, buffer(text_bynary), buffer(text_encoded), text_address, pointer_address, size))
			id += 1
cur.close()
conn.commit()
conn.close()

# REPOINTER (SQLITE3)
import sqlite3
conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
with open(filename2, 'r+b') as f:
	address = TEXT_BLOCK_START
	f.seek(TEXT_POINTER_BLOCK_START)
	cur.execute("SELECT text, new_text, address, pointer_address, id FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='clomax') AS t2 ON t1.id=t2.id_text")
	for row in cur:
		original_text = row[0]
		new_text = row[1]
		if (new_text):
			text = new_text
		else:
			text = original_text
		decoded_text = table.decode(text, True)
		curr_pointer_value = int_address2string_address(address, switch=True, shift=3)

		""" START DEBUG """
		with open("debug.txt", "a+b") as f2:
			f2.write(str(row[4]) + '\n')
			# pointer address - pointer value
			f2.write(str(row[3]) + ' - ' + str(row[2]) + '\n')
			f2.write(str(address) + '\n')
			f2.write(str(hex(f.tell())) + ' - ' + str(hex(string_address2int_address(curr_pointer_value, switch=True, offset=327680))) + '\n')
			f2.write(str(len(decoded_text)) + '\n')
			f2.write(str(len(original_text)) + '\n')
			f2.write(str(original_text) + '\n')				
			f2.write(str(new_text) + '\n')		
			if str(row[2]) != str(hex(string_address2int_address(curr_pointer_value, switch=True, offset=327680))):
				f2.write('WARNING!!!!!!!!\n')				
			f2.write("---------------------------\n")
		#sys.exit()
		""" STOP DEBUG """

		f.write(curr_pointer_value)	
		address += len(decoded_text)
cur.close()
conn.close()

#INSERTER (SQLITE3)
import sqlite3
conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
with open(filename2, 'r+b') as f:
	f.seek(TEXT_BLOCK_START)
	cur.execute("SELECT text, new_text, text_encoded, id FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='clomax') AS t2 ON t1.id=t2.id_text")
	for row in cur:
		original_text = row[0]
		new_text = row[1]
		if (new_text):
			text = new_text
		else:
			text = original_text
		decoded_text = table.decode(text, True)
		from django.utils.encoding import smart_str, smart_unicode
		f.write(smart_str(decoded_text))
		if f.tell() > TEXT_BLOCK_LIMIT:
			sys.exit('CRITICAL ERROR!!!')

		""" START DEBUG """
		with open("debug1.txt", "a+b") as f2:
			f2.write(str(row[3]) + '\n')
			if (len(row[0]) != len(table.decode(row[2], True))):
				f2.write('WARNING!!!!!!!!\n')
			if (len(smart_str(row[0])) != len(smart_str(table.decode(row[2], True)))):
				f2.write('WARNING2!!!!!!!!\n')
			if smart_str(row[0]) != smart_str(table.decode(row[2], True)):
				f2.write('WARNING3!!!!!!!!\n')				
			f2.write(row[0] + '\n')
			f2.write(str(len(row[0])) + '\n')
			f2.write(row[2] + '\n')
			f2.write(str(len(row[2])) + '\n')			
			f2.write(smart_str(row[2]) + '\n')
			f2.write(str(len(smart_str(row[2]))) + '\n')
			f2.write(smart_str(row[0]) + '\n')
			f2.write(str(len(smart_str(row[0]))) + '\n')		
			if (row[1]):
				f2.write(row[1] + '\n')
				f2.write(str(len(row[1])) + '\n')
			decoded_text = table.decode(row[0], True)
			f2.write(decoded_text + '\n')
			f2.write(str(len(decoded_text)) + '\n')
			decoded_text = table.decode(row[2], True)
			f2.write(decoded_text + '\n')
			f2.write(str(len(decoded_text)) + '\n')
			if (row[1]):
				decoded_text = table.decode(row[1], True)
				f2.write(decoded_text + '\n')
				f2.write(str(len(decoded_text)) + '\n')
			f2.write("---------------------------\n")
		#sys.exit()
		""" STOP DEBUG """
		
cur.close()
conn.close()

#CHECK
import sqlite3
conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
block = 0

with open(filename2, 'r+b') as f:
	f.seek(TEXT_BLOCK_START)
	cur.execute("SELECT text, new_text, text_encoded, id FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='clomax') AS t2 ON t1.id=t2.id_text")
	for row in cur:
		original_text = row[0]
		new_text = row[1]
		if (new_text):
			text = new_text
		else:
			text = original_text
		decoded_text = table.decode(text, True)
		block += len(decoded_text)
		
print TEXT_BLOCK_SIZE
print block

cur.close()
conn.close()