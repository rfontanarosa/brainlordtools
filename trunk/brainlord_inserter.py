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

def insert(f, block, start=TEXT_BLOCK_START, max=TEXT_BLOCK_MAX_SIZE):
	""" insert a block inside a file """
	print start
	if len(block) > max:
		print "the block is too large and it can't be inserted!"
	else:
		f.seek(start, SEEK_SET)
		f.write(block)

from brainlord_dumper import extract

filepath = sys.argv[1]

file = open(filepath, "rb+")
size = os.path.getsize(filepath)
f = mmap.mmap(file.fileno(), size)
file.close()
block = extract(f, start=TEXT_BLOCK_START, end=TEXT_BLOCK_LIMIT)
f.close()

f = open(filepath, "ab+")
insert(f, block, start=TEXT_BLOCK_START+1, max=TEXT_BLOCK_MAX_SIZE)
f.close()