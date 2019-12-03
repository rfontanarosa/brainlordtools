# -*- coding: utf-8 -*-

__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3, csv
from collections import OrderedDict

from rhtools.utils import crc32, byte2int, hex2dec, clean_text, int2hex, clean_text
from rhtools.Table import Table

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
TEXT_BLOCK1_END =  0x633d1
TEXT_BLOCK1_LIMIT = 0x633ff
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x633ff
TEXT_BLOCK2_START = 0x68000
TEXT_BLOCK2_END = TEXT_BLOCK2_LIMIT = 0x76ebf

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

def decode_text(text):
	text = text.replace(u'à', '{10}')
	text = text.replace(u'è', '{11}')
	text = text.replace(u'é', '{12}')
	text = text.replace(u'ì', '{13}')
	text = text.replace(u'ò', '{14}')
	text = text.replace(u'ù', '{15}')
	text = text.replace(u'È', '{16}')
	return text

def bof_dumper(args):
	""" DUMP """
	source_file = args.source_file
	table1_file = args.table1
	dump_path = args.dump_path
	db = args.database_file
	if crc32(source_file) != CRC32:
		sys.exit('SOURCE ROM CHECKSUM FAILED!')
	table1 = Table(table1_file)
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	id = 1
	with open(source_file, 'rb') as f:
		# READ POINTERS BLOCK 1
		block = 1
		pointers = OrderedDict()
		f.seek(POINTER_BLOCK1_START)
		while (f.tell() < POINTER_BLOCK1_END):
			paddress = f.tell()
			pvalue = f.read(2)
			taddress = struct.unpack('H', pvalue)[0] + TEXT_BLOCK1_START
			pointers.setdefault(taddress, []).append(paddress)
		# READ TEXT BLOCK 1
		for taddress, paddresses in pointers.iteritems():
			pointer_addresses = ';'.join(str(int2hex(x)) for x in paddresses)
			f.seek(taddress)
			text = read_text(f, end_byte=table1.getNewline())
			text_encoded = table1.encode(text, cmd_list=[0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c])
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
		# READ POINTERS BLOCK 2
		pointers = OrderedDict()
		f.seek(POINTER_BLOCK2_START)
		while(f.tell() < POINTER_BLOCK2_END):
			paddress = f.tell()
			pvalue = f.read(2)
			taddress = struct.unpack('H', pvalue)[0] + TEXT_BLOCK2_START
			pointers.setdefault(taddress, []).append(paddress)
		# READ TEXT BLOCK 2
		for taddress, paddresses in pointers.iteritems():
			pointer_addresses = ';'.join(str(int2hex(x)) for x in paddresses)
			f.seek(taddress)
			text = read_text(f, end_byte=table1.getNewline())
			text_encoded = table1.encode(text, cmd_list=[0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c])
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

def bof_inserter(args):
	""" INSERTER """
	dest_file = args.dest_file
	table2_file = args.table2
	db = args.database_file
	user_name = args.user
	table2 = Table(table2_file)
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(dest_file, 'r+b') as f:
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
					text = new_text if new_text else original_text
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

def bof_misc_inserter(args):
	dest_file = args.dest_file
	misc_file1 = args.misc_file1
	table3_file = args.table3
	table3 = Table(table3_file)
	with open(dest_file, 'r+b') as f:
		with open(misc_file1, 'rb') as csv_file:
			csv_reader = csv.DictReader(csv_file)
			for row in csv_reader:
				text_address = row.get('text_address')
				if text_address:
					text_address = int(text_address, 16)
					text = row.get('text')
					trans = row.get('trans') or text
					trans = trans.decode('utf8')
					#
					f.seek(text_address)
					decoded_text = table3.decode(text, mte_resolver=False, dict_resolver=False)
					trans = decode_text(trans)
					decoded_trans = table3.decode(trans, mte_resolver=False, dict_resolver=False)
					if len(decoded_trans) > len(decoded_text):
						print(int2hex(text_address))
					else:
						f.write(decoded_trans)

def bof_mte_finder(args):
	""" MTE FINDER """
	source_file = args.source_file
	table1_file = args.table1
	if crc32(source_file) != CRC32:
		sys.exit('SOURCE ROM CHECKSUM FAILED!')
	table1 = Table(table1_file)
	with open(source_file, 'rb') as f:
		# MTE POINTERS 1
		mte_pointers = []
		f.seek(DICT1_POINTER_BLOCK_START)
		while(f.tell() < DICT1_POINTER_BLOCK_END):
			p_offset = f.tell()
			p_bytes = f.read(2)
			p_value = DICT1_POINTER_BLOCK_START + (byte2int(p_bytes[1]) * 0x100) + byte2int(p_bytes[0])
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
				print('%s=%s' % (b, table1.encode(mte)))
			else:
				pass

def bof_mte_optimizer(args):
	""" MTE OPTIMIZER """
	dest_file = args.dest_file
	table1_file = args.table1
	table2_file = args.table2
	table3_file = args.table3
	mte_optimizer_path = args.mte_optimizer_path
	temp_path = args.temp_path
	db = args.database_file
	user_name = args.user
	table1 = Table(table1_file)
	# DICTIONARY OPTIMIZATION
	text_input_filename = os.path.join(temp_path, 'mteOptBoFText-input.txt')
	text_output_filename = os.path.join(temp_path, 'mteOptBofText-output.txt')
	#mte_optimizer_tool_filename = os.path.join(mte_optimizer_path, 'mteOpt.py')
	mte_optimizer_tool_filename = os.path.join(mte_optimizer_path, 'MTEOpt.exe')
	text_morpher_output_filename = os.path.join(temp_path, 'mteOptBoFText-morpher-output.txt')
	with open(text_input_filename, 'w') as out:
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
	#command = 'python %s -s "%s" -d "%s" -m 3 -M 12 -l 255 -o 768' % (mte_optimizer_tool_filename, text_input_filename, text_output_filename)
	command = '%s 3 10 "%s" "%s" 255' % (mte_optimizer_tool_filename, text_input_filename, text_morpher_output_filename)
	if sys.platform != 'win32':
		os.system("wine " + command)
	else:
		os.system(command)
	with open(text_morpher_output_filename, 'rU') as f1:
		with open(text_output_filename, 'w') as f2:
			for i, e in enumerate(f1):
				e = e.replace('\n', '').replace('\r', '')
				e = e.split('\t')
				n = hex(i + 768).rstrip('L')
				b = (n + '').replace('0x', '')
				b = b.zfill(4)
				line = "%s=%s" % (b, e[1][1:-1])
				f2.write(line + '\n')
	# TABLE OPTIMIZATION
	with open(table3_file, 'rU') as f:
		table3content = f.read()
		with open(text_output_filename, 'rU') as f2:
			mteOpt = f2.read()
			with open(table2_file, 'w') as f3:
				f3.write('\n' + table3content)
				f3.write('\n' + mteOpt)
	## DUMP
	values = []
	length = 0
	with open(text_output_filename, 'rb') as f:
		for line in f:
			parts = line.partition('=')
			value2 = parts[2]
			if value2:
				value2 = value2.replace('\n', '').replace('\r', '')
				values.append(value2)
				length += len(value2)
	# INSERTER
	with open(dest_file, 'r+b') as f:
		f.seek(DICT1_BLOCK_START)
		for i, value in enumerate(values):
			t_value = table1.decode(value, dict_resolver=False) + chr(0x03)
			if f.tell() + len(t_value) > (DICT1_BLOCK_LIMIT + 1):
				sys.exit('CRITICAL ERROR! MTE INSERTED: %d - TOTAL: %d!' % (i, len(values)))
			f.write(t_value)
	# REPOINTER
	with open(dest_file, 'r+b') as f:
		f.seek(DICT1_POINTER_BLOCK_START)
		length = 0
		for i, value in enumerate(values):
			p_value = struct.pack('H', DICT1_BLOCK_START + length - DICT1_POINTER_BLOCK_START)
			f.write(p_value)
			if f.tell() > (DICT1_POINTER_BLOCK_LIMIT + 1):
				sys.exit('CRITICAL ERROR! MTE REPOINTER!')
			length += (len(value) + 1)

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump', help='Execute DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
a_parser.set_defaults(func=bof_dumper)
b_parser = subparsers.add_parser('insert', help='Execute INSERTER')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
b_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
b_parser.add_argument('-u', '--user', action='store', dest='user', help='')
b_parser.set_defaults(func=bof_inserter)
c_parser = subparsers.add_parser('mte_finder', help='Execute MTE Finder')
c_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
c_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
c_parser.set_defaults(func=bof_mte_finder)
d_parser = subparsers.add_parser('mte_optimizer', help='Execute MTE Optimizer')
d_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
d_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
d_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
d_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Base original table without')
d_parser.add_argument('-mop', '--mte_optimizer_path', action='store', dest='mte_optimizer_path', help='MTE Optimizer path')
d_parser.add_argument('-tp', '--temp_path', action='store', dest='temp_path', help='Temporary path')
d_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
d_parser.add_argument('-u', '--user', action='store', dest='user', help='')
d_parser.set_defaults(func=bof_mte_optimizer)
e_parser = subparsers.add_parser('insert_misc', help='Execute INSERTER')
e_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
e_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Base table filename')
e_parser.add_argument('-m1', '--misc1', action='store', dest='misc_file1', help='MISC filename')
e_parser.set_defaults(func=bof_misc_inserter)
args = parser.parse_args()
args.func(args)
