__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, struct

SNES_HEADER_SIZE = 0x200

def pc2snes_lorom(offset):
    return ((offset * 2) & 0xFF0000) + (offset & 0x7FFF) + 0x8000

def snes2pc_lorom(offset):
    return (int(offset / 2) & 0xFF0000) + (offset & 0xFFFF) - 0x8000

def pc2snes_hirom(offset):
    return None if offset >= 0x400000 else offset | 0xc00000

def snes2pc_hirom(offset):
    return offset & 0x3FFFFF

def has_smc_header(filename):
    rest = os.stat(filename).st_size % 1024
    return False if rest == 0 else True if rest == 512 else None

def get_checksum(filename):
    checksum = b''
    with open(filename, 'rb') as f:
        data = f.read()
        checksum = sum(b for b in data)
        complement = ~checksum
        # checksum1 = struct.pack('H', checksum & 0xFFFF)
        # complement1 = struct.pack('H', complement & 0xFFFF)
    return(checksum)
