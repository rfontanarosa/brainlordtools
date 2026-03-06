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
    if rest == 0:
        return False
    if rest == 512:
        return True
    raise ValueError(f"Unexpected file size remainder: {rest} bytes. File may be corrupt.")

def decode_snes_addr(f, file_pos, base_addr=0xc00000, size=3, bank_byte=None):
    """
    Reads a SNES Bus Address from file_pos and converts it to a Physical File Offset.
    """
    f.seek(file_pos)
    raw = f.read(size)
    
    if len(raw) != size:
        return None

    if size == 3:
        # 24-bit Long Pointer
        bus_addr = int.from_bytes(raw, 'little')
    elif size == 2 and bank_byte is not None:
        # 16-bit Near Pointer + Bank Byte (e.g., b'\x80')
        bus_addr = int.from_bytes(raw + bank_byte, 'little')
    else:
        return None

    return bus_addr - base_addr

def encode_snes_addr(phys_offset, base_addr=0xc00000, size=3):
    """
    Converts a Physical File Offset back into SNES Bus Address bytes.
    """
    bus_addr = phys_offset + base_addr
    
    if size == 3:
        if bus_addr > 0xFFFFFF:
            raise ValueError(f"Address 0x{bus_addr:X} exceeds 24-bit range.")
        return struct.pack('<I', bus_addr)[:3]
    elif size == 2:
        if bus_addr > 0xFFFF:
            raise ValueError(f"Address 0x{bus_addr:X} exceeds 16-bit range.")
        return struct.pack('<H', bus_addr & 0xFFFF)

    raise ValueError("Size must be 2 or 3 bytes.")

def get_checksum(filename):
    checksum = b''
    with open(filename, 'rb') as f:
        data = f.read()
        checksum = sum(b for b in data)
        complement = ~checksum
        # checksum1 = struct.pack('H', checksum & 0xFFFF)
        # complement1 = struct.pack('H', complement & 0xFFFF)
    return(checksum)
