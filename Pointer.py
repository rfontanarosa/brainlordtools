__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

from os import SEEK_SET, SEEK_CUR, SEEK_END

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit("missing HexByteConversion module!")

from brainlord import *
	
class Pointer():

	def __init__(self, pointer):
		self._pointer = pointer
		self._addresses = []

	def __len__(self):
		return len(self._positions)

	def __str__(self):
		return str(self._pointer)

	def getFound(self):
		return self._addresses
		
	def find(self, f, start=SEEK_SET, previous_seek=None, in_range=True):
		"""  """
		f.seek(start)

		while True:
			# try to find the pointer inside the rom
			# TODO f.find should not use the HexToByte function to convert a pointer
			address = f.find(HexToByte(self._pointer), f.tell())
			if (address==-1):
				break
			else:
				# check if in_range option is enabled
				if in_range:
					# check it the address is in the range of is_valid_address
					if is_valid_address(address):
						self._addresses.append(address)
				if not in_range:
					self._addresses.append(address)
			# move the file handler to the next byte
			f.seek(address + 1)

		if previous_seek:
			f.seek(previous_seek)