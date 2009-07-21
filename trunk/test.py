__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys
import os
from os import SEEK_SET, SEEK_CUR, SEEK_END
import mmap

from Table import Table
from Dump import Dump

from brainlord import *

## TABLE

tablepath = sys.argv[3]
table = Table(tablepath)
print table


## DUMP

filepath = sys.argv[1]
file = open(filepath, "rb+")
size = os.path.getsize(filepath)
f = mmap.mmap(file.fileno(), size)
text_extracted = Dump.extract(f, TEXT_BLOCK_END, start=TEXT_BLOCK_START)
f.close()
file.close()

dump = Dump(dump=text_extracted)
dump.toTxt(table=table, filename="dump.txt", separated_byte_format=True)
#dump.toTxt(table=table, filename="dump2.txt", separated_byte_format=False)

dump2 = Dump()
dump2.fromTxt(table=table, filename="dump.txt", separated_byte_format=True)

print (TEXT_BLOCK_END - TEXT_BLOCK_START) + 1 == len(dump) == len(dump2)

"""
filepath2 = sys.argv[2]
file = open(filepath2, "ab+")
f = mmap.mmap(file.fileno(), size)
Dump.insert(f, text_extracted, TEXT_BLOCK_LIMIT, start=TEXT_BLOCK_START+1)
f.close()
file.close()
"""