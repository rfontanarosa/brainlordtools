__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os
from os import SEEK_SET, SEEK_CUR, SEEK_END

from Pointer import Pointer
from utils import byte2int, to_little_endian, dec2hex

class PointersTable():

	def __init__(self, file=None, start=SEEK_SET, previous_seek=None):

		self._pointers_table = []

		if file:
			file.seek(start)
			while True:
				byte = file.read(1)
				if not byte:
					break
				if 0xf7 == byte2int(byte):
					byte = file.read(1)
					if 0xf7 == byte2int(byte) == byte2int(byte):
						file.seek(file.tell())
					else:
						file.seek(file.tell()-1)

					offset = dec2hex(file.tell())
					pointer = Pointer(to_little_endian(offset))

					self._pointers_table.append(pointer)
			if previous_seek:
				file.seek(previous_seek)

	def add(self, pointer):
		if not isinstance(pointer, Pointer):
			raise TypeError, "Illegal argument type for built-in operation"
		return self._pointers_table.append(pointer)

	def __len__(self):
		return len(self._pointers_table)

	def __iter__(self):
		return self._pointers_table.__iter__()

	def __str__(self):
		string = ""
		for pointer in self._pointers_table:
			string += str(pointer) + "\n"
		return string

	def getUnResolvedPointers():
		"""  """
		unresolved_pointers = []
		for pointer in self._pointers_table:
			if not pointer.found:
				unresolved_pointers.append(pointer)
		return unresolved_pointers

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