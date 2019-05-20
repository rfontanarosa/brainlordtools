__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, mmap, struct, sqlite3
from collections import OrderedDict

from _rhtools.utils import *
from _rhtools.Table2 import Table

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--crc32check', action='store_true', default=False, help='Execute CRC32CHECK')
parser.add_argument('--dump', action='store_true', default=False, help='Execute DUMP')
parser.add_argument('--insert', action='store_true', default=False, help='Execute INSERTER')
parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
parser.add_argument('-d', '--dest',  action='store', dest='dest_file', required=True, help='Destination filename')
parser.add_argument('-t1', '--table1', action='store', dest='table1', required=True, help='Original table filename')
parser.add_argument('-t2', '--table2', action='store', dest='table2', required=True, help='Modified table filename')
parser.add_argument('-db', '--database',  action='store', dest='database_file', required=True, help='DB filename')
parser.add_argument('-u', '--user', action='store', dest='user', required=True, help='')
args = parser.parse_args()

execute_crc32check = args.crc32check
execute_dump = args.dump
execute_inserter = args.insert
filename = args.source_file
filename2 = args.dest_file
tablename = args.table1
tablename2 = args.table2
db = args.database_file
user_name = args.user
dump_path = 'brainlord/dump/'

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

CRC32 = 'AC443D87'

TEXT_BLOCK1_START = 0x170000
TEXT_BLOCK1_END = 0x17fac9
TEXT_BLOCK1_LIMIT = 0x17ffff
TEXT_BLOCK2_START = 0x120000
TEXT_BLOCK2_END = 0x0
TEXT_BLOCK2_LIMIT = 0x0

POINTER_BLOCK1_START = 0x50013
POINTER_BLOCK1_END = 0x50267
POINTER_BLOCK2_START = 0x6046e
POINTER_BLOCK2_END = 0x60593

table = Table(tablename)
table2 = Table(tablename2)

if execute_crc32check:
	""" CHECKSUM (CRC32) """
	if crc32(filename) != CRC32:
		sys.exit('ROM CHECKSUM: FAIL')
	else:
		print 'ROM CHECKSUM: OK'

if execute_dump:
	""" DUMP """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	id = 1
	#DUMP (TXTs + SQLITE3)
	with open(filename, 'rb') as f:
		# POINTERS 1
		pointers1 = OrderedDict()
		f.seek(POINTER_BLOCK1_START)
		while(f.tell() < POINTER_BLOCK1_END):
			paddress = f.tell()
			pValue1 = f.read(2)
			pValue1 = struct.unpack('H', pValue1)[0]
			pValue2 = f.read(1)
			pValue2 = (byte2int(pValue2) - 0xc0) * 0x10000
            print pValue2


			pValue = pValue2 + pValue1
			if pValue not in pointers1:
				pointers1[pValue] = []
			pointers1[pValue].append(paddress)
		# TEXT 1
		pointers2 = OrderedDict()
		for pointer in pointers1:
			pointer_addresses = ''
			for pointer_address in pointers1[pointer]:
				pointer_addresses += str(int2hex(pointer_address)) + ';'
			f.seek(pointer)
			text = b''
			byte = b'1'
			while not byte2int(byte) == table.getNewline():
				if byte2int(byte) == 0xf6:
					text += f.read(1)
				if byte2int(byte) == 0xfd or byte2int(byte) == 0xfe:
					text += f.read(2)
				if byte2int(byte) == 0xfb or byte2int(byte) == 0xfc or byte2int(byte) == 0xff:
					# POINTERS 2
					paddress = f.tell()
					if byte2int(byte) == 0xfb or byte2int(byte) == 0xfc:
						bytes = f.read(5)
						pValue1 = bytes[2:4]
						pValue2 = bytes[4]
						pValue1 = struct.unpack('H', pValue1)[0]
						pValue2 = (byte2int(pValue2) - 0xc0) * 0x10000
						pValue = pValue2 + pValue1
						if pValue not in pointers2:
							pointers2[pValue] = []
						pointers2[pValue].append(paddress)
						text += bytes
				byte = f.read(1)
				text += byte
			text_encoded = table.encode(text)
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(pointer)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, 1))
			# DUMP - TXT
			with open('%s - %d.txt' % (dump_path + str(id).zfill(3), len(pointers1[pointer])), 'w') as out:
				out.write(text_encoded)
				pass
			id += 1
		# TEXT 2
		pointers3 = OrderedDict()
		for pointer in pointers2:
			pointer_addresses = ''
			for pointer_address in pointers2[pointer]:
				pointer_addresses += str(int2hex(pointer_address)) + ';'
			f.seek(pointer)
			text = b''
			byte = b'1'
			while not byte2int(byte) == table.getNewline():
				if byte2int(byte) == 0xf6:
					text += f.read(1)
				if byte2int(byte) == 0xfd or byte2int(byte) == 0xfe:
					text += f.read(2)
				if byte2int(byte) == 0xfb or byte2int(byte) == 0xfc:
					# POINTERS 3
					paddress = f.tell()
					if byte2int(byte) == 0xfb or byte2int(byte) == 0xfc:
						bytes = f.read(5)
						pValue1 = bytes[2:4]
						pValue2 = bytes[4]
						pValue1 = struct.unpack('H', pValue1)[0]
						pValue2 = (byte2int(pValue2) - 0xc0) * 0x10000
						pValue = pValue2 + pValue1
						if pValue not in pointers3:
							pointers3[pValue] = []
						pointers3[pValue].append(paddress)
						text += bytes
				byte = f.read(1)
				text += byte
			text_encoded = table.encode(text)
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(pointer)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, 2))
			# DUMP - TXT
			with open('%s - %d.txt' % (dump_path + str(id).zfill(3), len(pointers2[pointer])), 'w') as out:
				out.write(text_encoded)
				pass
			id += 1
		# TEXT 3
		pointers4 = OrderedDict()
		for pointer in pointers3:
			pointer_addresses = ''
			for pointer_address in pointers3[pointer]:
				pointer_addresses += str(int2hex(pointer_address)) + ';'
			f.seek(pointer)
			text = b''
			byte = b'1'
			while not byte2int(byte) == table.getNewline():
				if byte2int(byte) == 0xf6:
					text += f.read(1)
				if byte2int(byte) == 0xfd or byte2int(byte) == 0xfe:
					text += f.read(2)
				if byte2int(byte) == 0xfb or byte2int(byte) == 0xfc:
					# POINTERS 4
					paddress = f.tell()
					bytes = f.read(5)
					pValue1 = bytes[2:4]
					pValue2 = bytes[4]
					pValue1 = struct.unpack('H', pValue1)[0]
					pValue2 = (byte2int(pValue2) - 0xc0) * 0x10000
					pValue = pValue2 + pValue1
					if pValue not in pointers4:
						pointers4[pValue] = []
					pointers4[pValue].append(paddress)
					text += bytes
				byte = f.read(1)
				text += byte
			text_encoded = table.encode(text)
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(pointer)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, 3))
			# DUMP - TXT
			with open('%s - %d.txt' % (dump_path + str(id).zfill(3), len(pointers3[pointer])), 'w') as out:
				out.write(text_encoded)
				pass
			id += 1
		# TEXT 4
		pointers5 = OrderedDict()
		for pointer in pointers4:
			pointer_addresses = ''
			for pointer_address in pointers4[pointer]:
				pointer_addresses += str(int2hex(pointer_address)) + ';'
			f.seek(pointer)
			text = b''
			byte = b'1'
			while not byte2int(byte) == table.getNewline():
				if byte2int(byte) == 0xf6:
					text += f.read(1)
				if byte2int(byte) == 0xfd or byte2int(byte) == 0xfe:
					text += f.read(2)
				if byte2int(byte) == 0xfb or byte2int(byte) == 0xfc:
					# POINTERS 4
					paddress = f.tell()
					bytes = f.read(5)
					pValue1 = bytes[2:4]
					pValue2 = bytes[4]
					pValue1 = struct.unpack('H', pValue1)[0]
					pValue2 = (byte2int(pValue2) - 0xc0) * 0x10000
					pValue = pValue2 + pValue1
					if pValue not in pointers5:
						pointers5[pValue] = []
					pointers5[pValue].append(paddress)
					text += bytes
				byte = f.read(1)
				text += byte
			text_encoded = table.encode(text)
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(pointer)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, 4))
			# DUMP - TXT
			with open('%s - %d.txt' % (dump_path + str(id).zfill(3), len(pointers4[pointer])), 'w') as out:
				out.write(text_encoded)
				pass
			id += 1
	cur.close()
	conn.commit()
	conn.close()

if execute_inserter:
	""" INSERTER """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(filename2, 'r+b') as f:
		# TEXT
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size, block FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text" % (user_name))
		for row in cur:
			# INSERTER
			id = row[3]
			original_text = row[2]
			new_text = row[4]
			address = row[5]
			size = row[7]
			block = row[8]
			if (new_text):
				text = new_text
			else:
				text = original_text
			decoded_text = table2.decode(text)
			if len(decoded_text) > size:
				sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - TEXT_LIMIT! %s > %s' % (id, block, len(decoded_text), size))
			address = hex2dec(address)
			f.seek(address)
			#f.write(decoded_text)
	cur.close()
	conn.close()