__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3

from rhtools.utils import hex2dec, clean_text
from rhtools.Table import Table

DICT1_POINTER_BLOCK_START = 0x180000
DICT1_POINTER_BLOCK_END = DICT1_POINTER_BLOCK_LIMIT = 0x1801ff
DICT1_BLOCK_START = 0x180200
DICT1_BLOCK_END = DICT1_BLOCK_LIMIT = 0x180fff

POINTER_BLOCK1_START = 0x188000
POINTER_BLOCK1_END = POINTER_BLOCK1_LIMIT =  0x0
POINTER_BLOCK2_START = 0x0
POINTER_BLOCK2_END = POINTER_BLOCK2_LIMIT = 0x188dff

POINTER_BLOCK_DISTANCE = 0x188000 - 0x77000

TEXT_BLOCK1_START = 0x190000
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x19ffff
TEXT_BLOCK2_START = 0x1a0000
TEXT_BLOCK2_END = TEXT_BLOCK2_LIMIT = 0x1affff

def bofBlockLimitsResolver(block):
	""" """
	blockLimits = (0, 0)
	if block == 1:
		blockLimits = (TEXT_BLOCK1_START, TEXT_BLOCK1_LIMIT, POINTER_BLOCK1_START, POINTER_BLOCK1_END, POINTER_BLOCK1_LIMIT)
	if block == 2:
		blockLimits = (TEXT_BLOCK2_START, TEXT_BLOCK2_LIMIT, POINTER_BLOCK2_START, POINTER_BLOCK2_END, POINTER_BLOCK2_LIMIT)
	return blockLimits

def bof_gemini_inserter(args):
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
		# BLOCK 1
		block = 1
		blockLimits = bofBlockLimitsResolver(block)
		TEXT_BLOCK_START = blockLimits[0]
		TEXT_BLOCK_LIMIT = blockLimits[1]
		#POINTER_BLOCK_START = blockLimits[2]
		#POINTER_BLOCK_END = blockLimits[3]
		#POINTER_BLOCK_LIMIT = blockLimits[4]
		POINTER_BLOCK_LIMIT = POINTER_BLOCK2_LIMIT
		f.seek(TEXT_BLOCK_START)
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, block))
		for row in cur:
			# INSERTER 1
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
				# REPOINTER 1
				pointer_addresses = row[6]
				if pointer_addresses:
					for pointer_address in pointer_addresses.split(';'):
						if pointer_address:
							pointer_address = hex2dec(pointer_address) + POINTER_BLOCK_DISTANCE
							f.seek(pointer_address)
							pvalue = struct.pack('H', new_text_address - TEXT_BLOCK_START)
							f.write(pvalue)
				f.seek(next_text_address)
		# BLOCK 2
		block = 2
		blockLimits = bofBlockLimitsResolver(block)
		TEXT_BLOCK_START = blockLimits[0]
		TEXT_BLOCK_LIMIT = blockLimits[1]
		#POINTER_BLOCK_START = blockLimits[2]
		#POINTER_BLOCK_END = blockLimits[3]
		POINTER_BLOCK_LIMIT = blockLimits[4]
		f.seek(TEXT_BLOCK_START)
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, block))
		for row in cur:
			# INSERTER 2
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
				# REPOINTER 2
				pointer_addresses = row[6]
				if pointer_addresses:
					for pointer_address in pointer_addresses.split(';'):
						if pointer_address:
							pointer_address = hex2dec(pointer_address) + POINTER_BLOCK_DISTANCE
							f.seek(pointer_address)
							pvalue = struct.pack('H', new_text_address - TEXT_BLOCK_START)
							f.write(pvalue)
							if pointer_address > (POINTER_BLOCK_LIMIT + 1):
								sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - POINTER_BLOCK_LIMIT! %s > %s (%s)' % (id, block, pointer_address, POINTER_BLOCK_LIMIT, (POINTER_BLOCK_LIMIT - pointer_address)))
				f.seek(next_text_address)
	cur.close()
	conn.close()

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
	# TODO use mte_optimizer.py instead of MTEOpt.exe for better performance and cross-platform compatibility
	# mte_optimizer_tool_filename = os.path.join(mte_optimizer_path, 'mte_optimizer.py')
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
b_parser = subparsers.add_parser('insert', help='Execute INSERTER')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
b_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
b_parser.add_argument('-u', '--user', action='store', dest='user', help='')
b_parser.set_defaults(func=bof_gemini_inserter)
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
args = parser.parse_args()
args.func(args)
