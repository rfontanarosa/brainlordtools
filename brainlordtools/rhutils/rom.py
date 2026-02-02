__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, zlib

def crc32(filename):
    prev = 0
    for line in open(filename, 'rb'):
        prev = zlib.crc32(line, prev)
    return '%X' % (prev & 0xFFFFFFFF)

def expand_rom(dest_file, size_in_bytes):
    with open(dest_file, 'r+b') as f:
        f.seek(0, os.SEEK_END)
        f.write(b'\x00' * size_in_bytes)
