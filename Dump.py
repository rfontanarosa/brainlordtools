__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = "r20"
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys
import mmap

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit("missing HexByteConversion module!")

from utils import *

from xml.dom.minidom import Document

class Dump():

	def __init__(self, dump=""):
		self._dump = dump
 
	def __str__(self):
		return self._dump.__str__()
 
	def __len__(self):
		return len(self._dump)
        
	def __cmp__ (self, dump):
		if not isinstance(dump, Dump):
			raise TypeError, "Illegal argument type for built-in operation"
		return self._dump == dump.getDump()

	def getDump(self):
		return self._dump

	def fromTxt(self, table=None, filename="dump.txt", separated_byte_format=True):
		with open(filename, "r") as f:
			if separated_byte_format:
				while True:
					byte = f.read(1)
					if not byte:
						break
					elif byte == "{":
						while "}" not in byte:
							byte += f.read(1)
						if byte == "{END}":
							f.read(1) # \n
							self._dump += int2byte(table.getNewline())
						else:
							found_in_table = table.find(byte[1:len(byte)-1])
							if found_in_table:
								self._dump += int2byte(found_in_table)
							else:
								self._dump += HexToByte(byte[1:len(byte)-1])
					else:
						self._dump += int2byte(table.find(byte))
			else:
				while True:
					byte = f.read(1)
					if not byte:
						break
					self._dump += byte

	def toTxt(self, table=None, filename="dump.txt", separated_byte_format=True):
		"""  """
		with open(filename, "w") as out:
			if table:
				for byte in self._dump:
					key = byte2int(byte) # byte2int
					if key in table:
						if separated_byte_format and (table.isDTE(key) or table.isMTE(key)):
							out.write("{%s}" % table[key])
						else:
							out.write(table[key])
					else:
						if separated_byte_format:
							out.write("{%s}" % ByteToHex(byte))
						else:
							out.write(byte)
			else:
				out.write(self._dump)

	def toXml(self, table, filename="dump.xml", separated_byte_format=True):
		"""  """
		doc = Document()
		root = doc.createElement("dump")
		elem = ""
		if table:
			with open(filename, "w") as out:
				for byte in self._dump:
					key = byte2int(byte) # byte2int			
					if key in table:
						if table.isNewline(key):
							text = doc.createElement("text")
							text.appendChild(doc.createCDATASection(elem))
							root.appendChild(text)
							elem = ""
						else:
							if separated_byte_format and (table.isDTE(key) or table.isMTE(key)):
								elem += "{%s}" % table[key]
							else:
								elem += (table[key])
					else:
						if separated_byte_format:
							elem += '{%s}' % ByteToHex(byte)
						else:
							elem += byte
				doc.appendChild(root)
				doc.writexml(out, '\n')
		else:
			pass
               
	@staticmethod
	def extract(f, start=0, end=0):
		""" extract data from a file """
		
		if end and start > end:
			raise Exception, "start address must be > to end address"
        
		text = ""
		  
		if isinstance(f, mmap.mmap):
			if not end:
				text = f[start:]
			if not start:
				text = f[:end]
			if start and end:
				text = f[start:end]

		if isinstance(f, file):
			f.tell(start)
			text = f2.read(end - start)

		return text

	@staticmethod
	def insert(f, dump, start=0, end=0):
		""" insert data into a file """

		if end and len(dump) > (end - start):
			raise Exception, "The dump is too large than the block and it can't be inserted!"
			
		if isinstance(f, mmap.mmap):
			if len(dump) > len(f[start:]):
				raise Exception, "The dump is too large than the file and it can't be inserted!"
			f.seek(start)
			f.write(dump)

		if isinstance(f, file):
			#todo condition for raise Exception, "The dump is too large than the file and it can't be inserted!"
			f.seek(start)
			f.write(dump)
			while(f.tell() < end):
				f.write("0")