__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys
import os
from os import SEEK_SET, SEEK_CUR, SEEK_END
import mmap

TEXT_BLOCK_START = 0x170000
TEXT_BLOCK_END = 0x17fac9
TEXT_BLOCK_LIMIT = 0x17ffff
TEXT_BLOCK_SIZE = (TEXT_BLOCK_END - TEXT_BLOCK_START) + 1
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

from Table import Table
from Dump import Dump


## TABLE

tablepath = sys.argv[2]
table = Table(tablepath)
print table


## DUMP

filepath = sys.argv[1]
file = open(filepath, "rb+")
size = os.path.getsize(filepath)
f = mmap.mmap(file.fileno(), size)
text_extracted = Dump.extract(f, TEXT_BLOCK_START, TEXT_BLOCK_END)
f.close()
file.close()

dump = Dump(dump=text_extracted)
dump.toTxt(table=table, filename="dump.txt", separated_byte_format=True)

dump2 = Dump()
dump2.fromTxt(table=table, filename="dump.txt", separated_byte_format=True)

print (TEXT_BLOCK_END - TEXT_BLOCK_START) + 1 == len(dump) == len(dump2)