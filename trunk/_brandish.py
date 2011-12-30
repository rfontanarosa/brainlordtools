__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys

import os
from os import SEEK_SET, SEEK_CUR, SEEK_END
import mmap

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit("missing HexByteConversion module!")

from utils import *

from xml.dom.minidom import *

from Table import Table
from Dump import Dump

TEXT_POINTER_BLOCK_START = 0x50d2a
TEXT_POINTER_BLOCK_END = 0x50fbd
TEXT_BLOCK_START = 0x50fbe
TEXT_BLOCK_END = 0x594ef
TEXT_BLOCK_LIMIT = 0x594ef

TEXT_BLOCK_SIZE = (TEXT_BLOCK_END - TEXT_BLOCK_START) + 1
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

#TEXT_ENTRIES = 330

filename = "roms/Brandish (U) [!].smc"
tablename = "tbls/Brandish (U) [!].tbl"
dumpname_txt = "dump/brandish_dump.txt"
dumpname_xml = "dump/brandish_dump.xml"

table = Table(tablename)

# DUMP TXT AND XML USING DUMP.PY
with open(filename, "rb+") as f:
	table = Table(tablename)
	map = mmap.mmap(f.fileno(), 0)
	text_extracted = Dump.extract(map, start=TEXT_BLOCK_START, end=TEXT_BLOCK_END)	
	dump = Dump(dump=text_extracted)
	dump.toTxt(table=table, filename="dump/brandish_dump2.txt")
	dump.toXml(table=table, filename="dump/brandish_dump2.xml")
	map.close()

# DUMP TXT
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
			with open(filename, "rb+") as f2:
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
				text = table.encode(text, separated_byte_format=True, encode_newline=True)
				out.write(text)
				
# DUMP XML
with open(filename, "rb+") as f:
	doc = Document()
	root = doc.createElement("root")
	root.setAttribute("file", filename)
	root.setAttribute("size", str(TEXT_BLOCK_SIZE))
	idx = 1
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
		with open(filename, "rb+") as f2:
			f2.seek(curr_pointer_value)
			if (next_pointer_value):
				size = next_pointer_value - curr_pointer_value
				text = f2.read(size)
			else:
				size = 0
				text = ""
				while True:
					b = f2.read(1)
					i = byte2int(b)
					size = size + 1
					if (i == 255):
						break
					else:
						text += b
			text = table.encode(text, separated_byte_format=True)
			elem = doc.createElement("text")
			elem.setAttribute("id", str(idx))
			elem.setAttribute("text_address", int2hex(curr_pointer_value))
			elem.setAttribute("pointer_address", int2hex(int(curr_pointer_address)))
			elem.setAttribute("size", str(size))
			if (next_pointer_value):
				elem.setAttribute("next_pointer_address", int2hex(int(curr_pointer_value) + size))
			cdata = doc.createCDATASection(text)
			#cdata = doc.createTextNode(text)
			elem.appendChild(cdata)
			root.appendChild(elem)
			idx = idx + 1
	doc.appendChild(root)
	with open(dumpname_xml, "wb") as out:
		doc.writexml(out, encoding="latin-1")

#DUMP TXTS
with open(filename, "rb+") as f:
	idx = 1
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
		with open(filename, "rb+") as f2:
			f2.seek(curr_pointer_value)
			if (next_pointer_value):
				size = next_pointer_value - curr_pointer_value
				text = f2.read(size)
			else:
				size = 0
				text = ""
				while True:
					b = f2.read(1)
					i = byte2int(b)
					size = size + 1
					if (i == 255):
						break
					else:
						text += b
			text = table.encode(text)
			text_encoded = table.encode(text, separated_byte_format=True)
			pointer_address = int2hex(int(curr_pointer_address))
			""" """
			with open("dump/" + str(idx) + ".txt", "w") as out:
				#out.write(text)
				out.write(text_encoded)
				pass
			""" """
			idx = idx + 1

#DUMP DB
import sqlite3
conn = sqlite3.connect('./db/brandish.db')
c = conn.cursor()
with open(filename, "rb+") as f:
	idx = 1
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
		with open(filename, "rb+") as f2:
			f2.seek(curr_pointer_value)
			if (next_pointer_value):
				size = next_pointer_value - curr_pointer_value
				text = f2.read(size)
			else:
				size = 0
				text = ""
				while True:
					b = f2.read(1)
					i = byte2int(b)
					size = size + 1
					if (i == 255):
						break
					else:
						text += b
			text = table.encode(text)
			text_encoded = table.encode(text, separated_byte_format=True)
			u = text.decode('latin-1')
			text_address = int2hex(curr_pointer_value)
			pointer_address = int2hex(int(curr_pointer_address))
			""" """
			c.execute("insert into texts values (?, ?, ?, ?, ?)", (idx, u, text_encoded, text_address, pointer_address))
			""" """
			idx = idx + 1
c.close()
conn.commit()
conn.close()

# INSERT XML
"""
with open("roms/Brandish2 (U) [!].smc", "ab+") as f:
	dom = parse(dumpname_xml)
	elements = dom.getElementsByTagName("text")
	print len(elements)
	for elem in elements:
		id = elem.getAttribute("id")
		text_address = elem.getAttribute("text_address")
		pointer_address = hex2dec(elem.getAttribute("pointer_address"))
		size = elem.getAttribute("size")
		f.seek(pointer_address)
		text = elem.firstChild.nodeValue
		#text = table.decode(text, separated_byte_format=False)
		#text = table.decode(text, separated_byte_format=True)
		#print text.encode('latin-1')
"""