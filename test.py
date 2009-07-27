__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys
import os
from os import SEEK_SET, SEEK_CUR, SEEK_END
import mmap

from HexByteConversion import ByteToHex
from HexByteConversion import HexToByte

from Table import Table
from Dump import Dump
from PointersTable import PointersTable
from Pointer import Pointer

from brainlord import *


## TABLE ##

tablepath = sys.argv[3]
table = Table(tablepath)
#print table


## DUMP ##

"""
filepath = sys.argv[1]
file = open(filepath, "rb+")
size = os.path.getsize(filepath)
f = mmap.mmap(file.fileno(), size)
text_extracted = Dump.extract(f, TEXT_BLOCK_END, start=TEXT_BLOCK_START)
f.close()
file.close()
"""

#dump = Dump(dump=text_extracted)
#dump.toTxt(table=table, filename="dump.txt", separated_byte_format=True)
#dump.toTxt(table=table, filename="dump2.txt", separated_byte_format=False)

#dump2 = Dump()
#dump2.fromTxt(table=table, filename="dump.txt", separated_byte_format=True)

#print (TEXT_BLOCK_END - TEXT_BLOCK_START) + 1 == len(dump) == len(dump2)


## INSERTION ##

"""
if sys.argv[2]:
	filepath2 = sys.argv[2]
	file = open(filepath2, "ab+")
	size = os.path.getsize(filepath2)
	f = mmap.mmap(file.fileno(), size)
	#Dump.insert(f, text_extracted, TEXT_BLOCK_LIMIT, start=TEXT_BLOCK_START+1)
	Dump.insert(f, dump2.getDump(), TEXT_BLOCK_LIMIT, start=TEXT_BLOCK_START)
	file.close()
	f.close()
"""


## REPOINTER ##

if sys.argv[4]:
	if sys.argv[4] == "-r":	
		file = open(sys.argv[1], "rb+")
		size = os.path.getsize(sys.argv[1])
		f = mmap.mmap(file.fileno(), size)
		
		file2 = open(sys.argv[2], "ab+")
		size2 = os.path.getsize(sys.argv[2])
		f2 = mmap.mmap(file2.fileno(), size2)		
		
		brainlord_repointer(f, f2)
		
		file2.close()
		f2.close()
		
		file.close()
		f.close()