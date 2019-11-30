__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3
from collections import OrderedDict

from rhtools.utils import byte2int
from rhtools.Table import Table

TEXT_BLOCK1_START = 0x318fb0
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x3307ff

def bof_gba_dumper(args):
	""" DUMP """
	source_file = args.source_file
	table1_file = args.table1
	dump_path = args.dump_path
	table1 = Table(table1_file)
	id = 1
	with open(source_file, 'rb') as f:
		f.seek(TEXT_BLOCK1_START)
		while(f.tell() < TEXT_BLOCK1_LIMIT):
			text = b''
			byte = b'1'
			while not byte2int(byte) == table1.getNewline():
				if byte2int(byte) in (0x03, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c):
					byte = f.read(1)
					text += byte
				byte = f.read(1)
				text += byte
			text_encoded = table1.encode(text, cmd_list=[0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c])
			# DUMP - DB
			text_binary = sqlite3.Binary(text)
			text_length = len(text_binary)
			block = 1
			# DUMP - TXT
			dump_file = os.path.join(dump_path, '%s.txt' % (str(id).zfill(4)))
			with open(dump_file, 'w') as out:
				out.write(text_encoded)
			id += 1

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump', help='Execute DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.set_defaults(func=bof_gba_dumper)
args = parser.parse_args()
args.func(args)
