__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = "r20"
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit("missing HexByteConversion module!")

from utils import *

import string

class Table():

	COMMENT_CHAR = ";"
	NEWLINE_CHAR = "/"
	BREAKLINE_CHAR = "*"

	def __init__(self, filename):

		self._table = {}
		self._dte = []
		self._mte = []
		self._newline = None
		self._breakline = None
		self._comments = []

		## tbl parser
		with open(filename, "r") as f:
			for line in f:
				line = line.strip("\n")
				# not comment
				if not line.startswith(Table.COMMENT_CHAR):
					# 
					if "=" in line:
						parts = line.partition("=")
						key = int(parts[0], 16)
						value = parts[2]
						self._table[key] = value
               # newline
					elif line.startswith(Table.NEWLINE_CHAR):
						self._newline = int(line[1:], 16)
						self._table[int(line[1:], 16)] = "\r" 
               # breakline
					elif line.startswith(Table.BREAKLINE_CHAR):
						self._breakline = int(line[1:len(line)], 16)
						self._table[int(line[1:len(line)], 16)] = "\n"
				else:
					self._comments.append(line[1:])

	def __iter__(self):
		return self._table.__iter__()

	def __str__(self):
		return self._table.__str__()

	def __len__(self):
		return len(self._table)

	def __getitem__(self, key):
		return self._table.__getitem__(key)

	def __contains__(self, key):
		return self._table.__contains__(key)

	def get(self, key):
		return self._table.get(key)

	def encode(self, text, separated_byte_format=False, encode_newline=False):
		decoded = ""
		if (text):
			for byte in text:
				key = byte2int(byte)
				if (not encode_newline and self.isNewline(key)):
					pass
				else:
					if key in self:
						if separated_byte_format and (self.isDTE(key) or self.isMTE(key)):
							decoded += "{%s}" % self[key]
						else:
							decoded += (self[key])
					else:
						if separated_byte_format:
							decoded += '{%s}' % ByteToHex(byte)
						else:
							decoded += byte
		return decoded

	def decode(self, text, separated_byte_format=False):
		encoded = ""
		if (text):
			if separated_byte_format:
				pass
			else:
				for byte in text:
					key = self.find(byte)
					if (key):
						encoded += self.get(key)
					else:
						encoded += byte
		return encoded

	def isDTE(self, key):
		""" Check if the element is a DTE (Dual Tile Encoding) """
		return self.get(key) and len(self.get(key)) == 2 and not self.isNewline(key) and not self.isBreakline(key)

	def isMTE(self, key):
		""" Check if the element is a MTE (Multi Tile Encoding) """
		return self.get(key) and len(self.get(key)) >= 2 and not self.isNewline(key) and not self.isBreakline(key)

	def getDTEs(self):
		return self._dte

	def getMTEs(self):
		return self._mte

	def isNewline(self, key):
		return self._newline == key

	def isBreakline(self, key):
		return self._breakline == key

	def getNewline(self):
		return self._newline

	def getBreakline(self):
		return self._breakline

	def getComments(self):
		return self._comments
		
	def find(self, value):
		k = None
		for key in self._table.keys():
			if self.get(key) == value:
				if k:
					raise Exception, "Two instance of %s found!" % value
				k = key
		return k