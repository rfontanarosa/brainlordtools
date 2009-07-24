__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

TEXT_BLOCK_START = 0x170000
TEXT_BLOCK_END = 0x17fac9
TEXT_BLOCK_LIMIT = 0x17ffff
TEXT_BLOCK_SIZE = (TEXT_BLOCK_END - TEXT_BLOCK_START) + 1
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

TEXT_POINTER1_BLOCK_START = 0xf9e
TEXT_POINTER1_BLOCK_END = 0xfef

TEXT_POINTER2_BLOCK_START = 0x50010
TEXT_POINTER2_BLOCK_END = 0x55567

## there are 20 (?) pointers in this block and every pointer starts with 0x01
#FAERIES_POINTER_START_BYTE = 0x01
FAERIES_POINTER_BLOCK_START = 0x18ea0
FAERIES_POINTER_BLOCK_END = 0x18f9b

def is_valid_address(address):
	"""  """
	return (TEXT_POINTER1_BLOCK_END >= address >= TEXT_POINTER1_BLOCK_START) \
			or (TEXT_POINTER2_BLOCK_END >= address >= TEXT_POINTER2_BLOCK_START) \
			or (FAERIES_POINTER_BLOCK_END >= address >= FAERIES_POINTER_BLOCK_START) \
			or (TEXT_BLOCK_END >= address >= TEXT_BLOCK_START)

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit("missing HexByteConversion module!")

import os
from os import SEEK_SET, SEEK_CUR, SEEK_END

class Pointer():

    def __init__(self, pointer):
        self._pointer = pointer
        self._addresses = []

    def __len__(self):
    	return len(self._addresses)

    def __str__(self):
    	return str(self._pointer)

	def __getitem__(self, index):
		if isinstance(index, slice):
			return [x**2 for x in range(index.start, index.stop, index.step)]
		else:
			return index**2

    def setFound(self, addresses):
        if isinstance(index, list):
			self._adresses = adresses
			return True
        else:
            return False

    def getFound(self):
        return self._addresses

    def find(self, f, start=SEEK_SET, in_range=True, previous_seek=None):
    	# move file handler to star position
        f.seek(start)
    	while True:
    		# try to find the pointer inside the rom
    		address = f.find(HexToByte(self._pointer), f.tell())
    		if (address==-1):
    			break
    		else:
    			# check if in_range option is enabled
    			if in_range:
    				# check if the address is in the range of is_valid_address
    				if is_valid_address(address):
    					self._addresses.append(address)
    			if not in_range:
    				self._addresses.append(address)
    		# move file handler to next byte
    		f.seek(address + 1)
        # move file handler to previous byte if previous_seek set
    	if previous_seek:
    		f.seek(previous_seek)