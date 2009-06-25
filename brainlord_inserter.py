"""
brainlord_inserter
version: 0.1 (2009-04-14)
changes: initial version
author: roberto fontanarosa (robertofontanarosa@hotmail.com)
"""

#import mmap
#import os
import sys
#from os import SEEK_SET, SEEK_CUR, SEEK_END
#import pdb

import brainlord_table
#import brainlord_dumper

TEXT_BLOCK_START = 0x170000
TEXT_BLOCK_END = 0x17fac9
TEXT_BLOCK_LIMIT = 0x17ffff
TEXT_BLOCK_SIZE = TEXT_BLOCK_END - TEXT_BLOCK_START
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

def insert(f, block, start=TEXT_BLOCK_START, max=TEXT_BLOCK_MAX_SIZE):
	""" insert a text block inside a file """
	if len(block) > max:
		print 'text to insert is too large!'
	else:
		f.seek(TEXT_BLOCK_START)
		f.write(block)

# text block creation from a txt dump file
try:
	f = open('dump.txt', 'rb+')
except IOError:
	sys.exit('file not found!')
while True:
	byte = f.read(1)
	
	if not byte:
		break
		
	if byte == '{':
		tag_string = ''
		while True:
			tag_byte = f.read(1)
			if tag_byte != '}':
				tag_string += tag_byte
				continue
			else:
				break
		# tag_string to be transformed in a byte checking if it's a dte
		print(tag_string)
		
f.close()