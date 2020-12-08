__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3
from collections import OrderedDict

from rhtools.utils import crc32, int2byte, int2hex, byte2int, hex2dec
from rhtools.Table import Table

from rhtools.HexByteConversion import ByteToHex

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

CRC32 = '8C2068D1'

POINTER_BLOCKS = (
	(0x930, 0x97d),
	(0x10104, 0x10109),
	(0x1010c, 0x10133),
	(0x10468, 0x10497),
	(0x1068e, 0x106ad),
	(0x1228f, 0x122ae),
	(0x12628, 0x12657)
)

POINTER_BLOCK_START = 0x62003
#POINTER_BLOCK_END = POINTER_BLOCK_LIMIT = 0x622b4
POINTER_BLOCK_END = POINTER_BLOCK_LIMIT = 0x622c3

TEXT_BLOCK1_START = 0x6277a
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x19ffff

EXP_START = 0x107f50

def spike_read_text(f, end_byte=0x00):
	text = b''
	byte = b'1'
	while not byte2int(byte) == end_byte:
		if byte2int(byte) == 0xf4:
			byte = f.read(1)
			text += byte
		if byte2int(byte) == 0xfa:
			byte = f.read(3)
			text += byte
		byte = f.read(1)
		text += byte
	return text

def pointerValue2bytes(pointer):
	"""  """
	pStr = format(pointer + 0x900000, 'x')
	pBytes = bytearray.fromhex(pStr)
	return int2byte(pBytes[2]) + int2byte(pBytes[1]) + int2byte(pBytes[0])

def spike_dumper(args):
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
		pointers = OrderedDict()
		for pointer_block in POINTER_BLOCKS:
			f.seek(pointer_block[0])
			while f.tell() < pointer_block[1]:
				p_offset = f.tell()
				pointer = f.read(2)
				p_value = struct.unpack('H', pointer)[0] + 0x10000 - 0x8000
				if p_value > 0:
					pointers.setdefault(p_value, []).append(p_offset)
		# TEXT POINTERS
		f.seek(POINTER_BLOCK_START)
		while f.tell() < POINTER_BLOCK_END:
			p_offset = f.tell()
			pointer = f.read(3)
			p_value = struct.unpack('i', pointer[:3] + '\x00')[0] - 0x868000
			if p_value > 0:
				pointers.setdefault(p_value, []).append(p_offset)
		# TEXT 1
		for taddress, paddresses in pointers.iteritems():
			pointer_addresses = ';'.join(str(int2hex(x)) for x in paddresses)
			f.seek(taddress)
			text = b''
			text = spike_read_text(f, end_byte=table1.getNewline())
			text_encoded = table1.encode(text, cmd_list=[(0xf4, 2), (0xf6, 1), (0xf8, 1), (0xfa, 4), (0xfc, 1), (0xfe, 1), (0xff, 1)])
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(taddress)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, 1, id))
			# DUMP - TXT
			"""
			with open('%s - %d.txt' % (dump_path + str(id).zfill(4), len(pointers[pointer])), 'w') as out:
				out.write(text_encoded)
				pass
			"""
			id += 1
		cur.close()
		conn.commit()
		conn.close()

def spike_inserter(args):
	""" EXPANDER """
	with open(filename2, 'r+b') as f:
		f.seek(EXP_START)
		f.write(int2byte(0) * 32768)
	""" INSERTER """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(filename2, 'r+b') as f:
		f.seek(EXP_START)
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, 1))
		for row in cur:
			# INSERTER
			id = row[3]
			original_text = row[2]
			new_text = row[4]
			if (new_text):
				text = new_text
			else:
				text = original_text
			decoded_text = table2.decode(text)
			new_text_address = f.tell()
			f.seek(new_text_address)
			f.write(decoded_text)
			next_text_address = f.tell()
			# REPOINTER
			pointer_addresses = row[6]
			if pointer_addresses:
				for pointer_address in pointer_addresses.split(';'):
					if pointer_address:
						pointer_address = hex2dec(pointer_address)
						f.seek(pointer_address)
						pvalue = pointerValue2bytes(new_text_address)
						f.write(pvalue)
			f.seek(next_text_address)
	cur.close()
	conn.close()

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump', help='Execute DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
a_parser.set_defaults(func=spike_dumper)
b_parser = subparsers.add_parser('insert', help='Execute INSERTER')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
b_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
b_parser.add_argument('-u', '--user', action='store', dest='user', help='')
b_parser.set_defaults(func=spike_inserter)
args = parser.parse_args()
args.func(args)
