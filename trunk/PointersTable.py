__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os
from os import SEEK_SET, SEEK_CUR, SEEK_END
import mmap

from Pointer import Pointer
from utils import byte2int, to_little_endian, dec2hex
from brainlord import *

class PointersTable():

	def __init__(self, f, start=SEEK_SET, previous_seek=None):

		self._pointers_table = []

		f.seek(start)
		while True:
			byte = f.read(1)
			if not byte:
				break
			if 0xf7 == byte2int(byte):
				byte = f.read(1)
				if 0xf7 == byte2int(byte) == byte2int(byte):
					f.seek(f.tell())
				else:
					f.seek(f.tell()-1)
					
				offset = dec2hex(f.tell())
				pointer = Pointer(to_little_endian(offset))
				
				self._pointers_table.append(pointer)
		if previous_seek:
			f.seek(previous_seek)

	def __len__(self):
		return len(self._pointers_table)

	def __str__(self):
		string = ""
		for pointer in self._pointers_table:
			string += str(pointer) + "\n"
		return string

	def resolvePointers(self, f, start=SEEK_SET, previous_seek=None, in_range=True):
		"""  """
		for pointer in self._pointers_table:
			pointer.find(f, start, previous_seek, in_range)
				
	def toTxt(self, filename="pointers_table.txt"):
		f = open(filename, "w")
		for pointer in self._pointers_table:
			f.write(str(pointer))
			found = pointer.getFound()
			for address in found:
				f.write("\t" + str(address))
			f.write("\n")
		f.close()