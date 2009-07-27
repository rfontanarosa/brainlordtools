__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys
import os
import mmap

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit("missing HexByteConversion module!")

from PointersTable import PointersTable
from Pointer import Pointer

# TODO trovare un modo per verificare se e presente o meno l'header
# TODO aggiungere agli indirizzi i byte dell'header SE questo e presente
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


def is_shop_pointer(address):
	"""  """
	return (0x25000 >= address >= 0x23000)


def is_in_text_block(address):
	"""  """
	return (TEXT_BLOCK_END >= address >= TEXT_BLOCK_START)


def brainlord_repointer(f, filename2):
	"""  """

	file2 = open(filename2, "ab+")
	size2 = os.path.getsize(filename2)
	f2 = mmap.mmap(file2.fileno(), size2)
	
	pointers_table = PointersTable(file=f, start=TEXT_BLOCK_START)
	pointers_table.resolvePointers(f)
	pointers_table.toTxt(filename="pointers_table.txt")
	pointers_table2 = PointersTable(file=f2, start=TEXT_BLOCK_START)
	pointers_table2.toTxt(filename="pointers_table2.txt")
	shop_pointers_table = PointersTable()

	if len(pointers_table)==len(pointers_table2):
	
		for pointer, pointer2 in zip(pointers_table, pointers_table2):
		
            # if the pointer has not been found it could be a shop pointer
			if not pointer.getFound():
				## shop_repointer - create, found and add a shop pointer in shop_pointer table
				shop_pointer = Pointer("a9" + str(pointer)[0:4:1])
				shop_pointer.find(f, in_range=False)
				new_shop_pointer = Pointer("a9" + str(pointer2)[0:4:1])
				new_shop_pointer.setFound(shop_pointer.getFound())
				shop_pointers_table.add(new_shop_pointer)
			
			#
			if pointer.getFound():
				## text_repointer
				for address in pointer.getFound():
					if is_valid_address(address):
						if is_in_text_block(address):
							new_pointer = Pointer(str(pointer))			
							new_pointer.find(f2, start=TEXT_BLOCK_START)
							if new_pointer.getFound():
								for new_address in new_pointer.getFound():
									f2.seek(new_address)
									f2.write(HexToByte(str(pointer2)))
						if not is_in_text_block(address):
							f2.seek(address)
							f2.write(HexToByte(str(pointer2)))

					else:
						pass

		for shop_pointer in shop_pointers_table:
			if shop_pointer.getFound():
				for new_shop_address in shop_pointer.getFound():
					if is_shop_pointer(new_shop_address):
						f2.seek(new_shop_address)
						f2.write(HexToByte(str(shop_pointer)))
					else:
						pass
			else:
				pass
	
		#shop_pointers_table.toTxt(filename="shop_pointers.txt")
				
		file2.close()
		f2.close()
	
	else:
		sys.exit('DRAMATIC ERROR! array of original pointers is not alligned with the array of modified pointers')		