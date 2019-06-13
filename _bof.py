__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3
from collections import OrderedDict

from _rhtools.utils import *
from _rhtools.Table2 import Table

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--crc32check', action='store_true', default=False, help='Execute CRC32CHECK')
parser.add_argument('--dump', action='store_true', default=False, help='Execute DUMP')
parser.add_argument('--insert', action='store_true', default=False, help='Execute INSERTER')
parser.add_argument('--mte_finder', action='store_true', default=False, help='Find MTE')
parser.add_argument('--mte_optimizer', action='store_true', default=False, help='Optimize MTE')
parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
parser.add_argument('-d', '--dest',  action='store', dest='dest_file', required=True, help='Destination filename')
parser.add_argument('-t1', '--table1', action='store', dest='table1', required=True, help='Original table filename')
parser.add_argument('-t2', '--table2', action='store', dest='table2', required=True, help='Modified table filename')
parser.add_argument('-t3', '--table3', action='store', dest='table3', required=False, help='Base original table without')
parser.add_argument('-db', '--database',  action='store', dest='database_file', required=True, help='DB filename')
parser.add_argument('-u', '--user', action='store', dest='user', required=True, help='')
args = parser.parse_args()

execute_crc32check = args.crc32check
execute_dump = args.dump
execute_inserter = args.insert
execute_mtefinder = args.mte_finder
execute_mteoptimizer = args.mte_optimizer
filename = args.source_file
filename2 = args.dest_file
tablename = args.table1
tablename2 = args.table2
tablename3 = args.table3
db = args.database_file
user_name = args.user
dump_path = 'bof/dump/'

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

CRC32 = 'C788B696'

DICT1_POINTER_BLOCK_START = 0x63400
DICT1_POINTER_BLOCK_END = DICT1_POINTER_BLOCK_LIMIT = 0x635ff
DICT1_BLOCK_START = 0x63600
DICT1_BLOCK_END = DICT1_BLOCK_LIMIT = 0x63e04

POINTER_BLOCK1_START = 0x77000
POINTER_BLOCK1_END = POINTER_BLOCK1_LIMIT = 0x7723f
POINTER_BLOCK2_START = 0x77240
POINTER_BLOCK2_END = POINTER_BLOCK2_LIMIT = 0x77dff

TEXT_BLOCK1_START = 0x60000
#TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x633d1
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x633ff
TEXT_BLOCK2_START = 0x68000
TEXT_BLOCK2_END = TEXT_BLOCK2_LIMIT = 0x76ebf

table = Table(tablename)
table2 = Table(tablename2)

def bofBlockLimitsResolver(block):
	""" """
	blockLimits = (0, 0)
	if block == 1:
		blockLimits = (TEXT_BLOCK1_START, TEXT_BLOCK1_LIMIT, POINTER_BLOCK1_START, POINTER_BLOCK1_END, POINTER_BLOCK1_LIMIT)
	if block == 2:
		blockLimits = (TEXT_BLOCK2_START, TEXT_BLOCK2_LIMIT, POINTER_BLOCK2_START, POINTER_BLOCK2_END, POINTER_BLOCK2_LIMIT)
	return blockLimits

def read_text(f, end_byte=0x00):
	text = b''
	byte = b'1'
	while not byte2int(byte) == end_byte:
		if byte2int(byte) in (0x03, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c):
			byte = f.read(1)
			text += byte
		byte = f.read(1)
		text += byte
	return text

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
	with open(filename, 'rb') as f:
		# TEXT POINTERS 1
		block = 1
		pointers = OrderedDict()
		f.seek(POINTER_BLOCK1_START)
		while (f.tell() < POINTER_BLOCK1_END):
			paddress = f.tell()
			pvalue = f.read(2)
			taddress = struct.unpack('H', pvalue)[0] + 0x60000
			pointers.setdefault(taddress, []).append(paddress)
		# TEXT 1
		for taddress, paddresses in pointers.iteritems():
			pointer_addresses = ';'.join(str(int2hex(x)) for x in paddresses)
			f.seek(taddress)
			text = read_text(f, end_byte=table.getNewline())
			text_encoded = table.encode(text, cmd_list=[0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c])
			# DUMP - DB
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(taddress)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, block))
			"""
			# DUMP - TXT
			with open('%s - %d.txt' % (dump_path + str(id).zfill(4), len(paddresses)), 'w') as out:
				out.write(text_encoded)
			"""
			id += 1
		block = 2
		# TEXT POINTERS 2
		pointers = OrderedDict()
		f.seek(POINTER_BLOCK2_START)
		while(f.tell() < POINTER_BLOCK2_END):
			paddress = f.tell()
			pvalue = f.read(2)
			taddress = struct.unpack('H', pvalue)[0] + 0x68000
			pointers.setdefault(taddress, []).append(paddress)
		# TEXT 2
		for taddress, paddresses in pointers.iteritems():
			pointer_addresses = ';'.join(str(int2hex(x)) for x in paddresses)
			f.seek(taddress)
			text = read_text(f, end_byte=table.getNewline())
			text_encoded = table.encode(text, cmd_list=[0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c])
			# DUMP - DB
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(taddress)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, block))
			"""
			# DUMP - TXT
			with open('%s - %d.txt' % (dump_path + str(id).zfill(4), len(paddresses)), 'w') as out:
				out.write(text_encoded)
			"""
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
		for block in range(1, 3):
			blockLimits = bofBlockLimitsResolver(block)
			TEXT_BLOCK_START = blockLimits[0]
			TEXT_BLOCK_LIMIT = blockLimits[1]
			POINTER_BLOCK_START = blockLimits[2]
			POINTER_BLOCK_END = blockLimits[3]
			POINTER_BLOCK_LIMIT = blockLimits[4]
			# BLOCK X
			f.seek(TEXT_BLOCK_START)
			cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, block))
			for row in cur:
				# INSERTER X
				id = row[3]
				if id not in (207, 444):
					original_text = row[2]
					new_text = row[4]
					if (new_text):
						text = new_text
					else:
						text = original_text
					decoded_text = table2.decode(text)
					new_text_address = f.tell()
					if new_text_address + len(decoded_text) > (TEXT_BLOCK_LIMIT + 1):
						sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - TEXT_BLOCK_LIMIT! %s > %s (%s)' % (id, block, next_text_address + len(decoded_text), TEXT_BLOCK_LIMIT, (TEXT_BLOCK_LIMIT - next_text_address - len(decoded_text))))
					f.seek(new_text_address)
					f.write(decoded_text)
					next_text_address = f.tell()
					# REPOINTER X
					pointer_addresses = row[6]
					if pointer_addresses:
						for pointer_address in pointer_addresses.split(';'):
							if pointer_address:
								pointer_address = hex2dec(pointer_address)
								f.seek(pointer_address)
								pvalue = struct.pack('H', new_text_address - TEXT_BLOCK_START)
								f.write(pvalue)
								if pointer_address > (POINTER_BLOCK_LIMIT + 1):
									sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - POINTER_BLOCK_LIMIT! %s > %s (%s)' % (id, block, pointer_address, POINTER_BLOCK_LIMIT, (POINTER_BLOCK_LIMIT - pointer_address)))
					f.seek(next_text_address)
	cur.close()
	conn.close()

if execute_mtefinder:
	""" MTE FINDER """
	with open(filename, 'rb') as f:
		# MTE POINTERS 1
		mte_pointers = []
		f.seek(DICT1_POINTER_BLOCK_START)
		while(f.tell() < DICT1_POINTER_BLOCK_END):
			p_offset = f.tell()
			p_bytes = f.read(2)
			p_value = 0x63400 + (byte2int(p_bytes[1]) * 0x100) + byte2int(p_bytes[0])
			pointer = {'offset':p_offset, 'bytes':p_bytes, 'value':p_value}
			mte_pointers.append(pointer)
		for i, p in enumerate(mte_pointers):
			size = len(mte_pointers) - 1
			if i < size:
				f.seek(mte_pointers[i]['value'])
				mte = ''
				byte = b'1'
				while not byte2int(byte) == 0x03:
					byte = f.read(1)
					if byte2int(byte) != 0x03:
						mte += byte
				b = (int2hex(i + 0x300) + '').replace('x', '')
				print '%s=%s' % (b, table.encode(mte))
			else:
				pass

if execute_mteoptimizer:
	""" MTE OPTIMIZER """
	# DICTIONARY OPTIMIZATION
	with open('mteOptBoFText-input.txt', 'w') as out:
		conn = sqlite3.connect(db)
		conn.text_factory = str
		cur = conn.cursor()
		cur.execute("SELECT text_encoded, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text" % user_name)
		for row in cur:
			new_text = row[1]
			original_text = row[0]
			text = new_text if new_text else original_text
			text = text.replace('{04}', '\n')
			text = clean_text(text)
			out.write(text + '\n')
	os.system("mteOpt.py -s \"mteOptBoFText-input.txt\" -d \"mteOptBoFText-output.txt\" -m 3 -M 12 -l 255 -o 768")
	# TABLE OPTIMIZATION
	with open(tablename3, 'rU') as f:
		table3content = f.read()
		with open('mteOptBoFText-output.txt', 'rU') as f2:
			mteOpt = f2.read()
			with open(tablename2, 'w') as f3:
				f3.write('\n' + table3content)
				f3.write('\n' + mteOpt)
	## DUMP
	values = []
	length = 0
	with open('mteOptBoFText-output.txt', 'rb') as f:
		for line in f:
			parts = line.partition('=')
			value1 = parts[0]
			value2 = parts[2]
			if value2:
				value2 = value2.replace('\n', '').replace('\r', '')
				values.append(value2)
				length += len(value2)
	# INSERTER
	with open(filename2, 'r+b') as f:
		f.seek(DICT1_BLOCK_START)
		for i, value in enumerate(values):
			t_value = table.decode(value, dict_resolver=False) + chr(0x03)
			if f.tell() + len(t_value) > (DICT1_BLOCK_LIMIT + 1):
				sys.exit('CRITICAL ERROR! MTE INSERTED: %d - TOTAL: %d!' % (i, len(values)))
			f.write(t_value)
	# REPOINTER
	with open(filename2, 'r+b') as f:
		f.seek(DICT1_POINTER_BLOCK_START)
		length = 0
		for i, value in enumerate(values):
			p_value = struct.pack('H', DICT1_BLOCK_START + length - DICT1_POINTER_BLOCK_START)
			f.write(p_value)
			if f.tell() > (DICT1_POINTER_BLOCK_LIMIT + 1):
				sys.exit('CRITICAL ERROR! MTE REPOINTER!')
			length += (len(value) + 1)