__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import pathlib
import sys

from rhutils.table import Table


# ============================================================
# ROM REGION CONSTANTS (all file offsets, headerless ROM)
# ============================================================

REGIONS = {
    'english_menu': {
        'bank_start':       0x140000,
        'ptr_table_start':  0x140000,
        'ptr_table_end':    0x1400D7,  # inclusive
        'bank_read_size':   0x008000,
        'section':          'menu',
    },
    'english_dialogue': {
        'bank_start':       0x110000,
        'ptr_table_start':  0x110000,
        'ptr_table_end':    0x110C02,  # inclusive
        'bank_read_size':   0x030000,
        'ptr_size':         3,          # 24-bit SNES addresses
        'section':          'dialogue',
    },
}


# ============================================================
# CUSTOM CONTROL CODE HANDLERS
# Signature: (data: bytes, i: int) -> (consumed: int, text: str)
# where i is the index of the first byte AFTER the command byte,
# and consumed is the number of bytes read starting from i.
# ============================================================

def _decode_40(data, i):
    if i >= len(data):
        return 0, '<40>'
    sub = data[i]

    no_arg_subs = {
        0x00, 0x01, 0x02, 0x03, 0x05, 0x0E, 0x0F, 0x13, 0x15,
        0x18, 0x1A, 0x1C, 0x1D, 0x23, 0x24, 0x26, 0x27, 0x28,
        0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x35, 0x37,
        0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40,
        0x43, 0x44, 0x45, 0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x4F,
        0x50, 0x51, 0x52, 0x54, 0x55, 0x56, 0x59, 0x5D, 0x5E,
        0x5F, 0x60, 0x61, 0x62, 0x64, 0x65, 0x66, 0x67, 0x6A,
        0x6B, 0x6D, 0x6E, 0x6F, 0x70, 0x71, 0x72, 0x74, 0x75,
        0x79, 0x93, 0xE1, 0xEE,
    }
    one_arg_subs = {
        0x11, 0x12, 0x17, 0x19, 0x1B, 0x1F, 0x21, 0x25,
        0x36, 0x42, 0x46, 0x47, 0x4D, 0x4E, 0x57, 0x63,
        0x69, 0x6C, 0x73, 0x77, 0x78, 0xE9,
    }
    two_arg_subs = {
        0x1E, 0x29, 0x31, 0x33, 0x34, 0x58, 0x5B, 0x5C, 0x9E,
    }
    three_arg_subs = {0x68}

    if sub in no_arg_subs:
        return 1, f'<40,{sub:02X}>'
    elif sub in one_arg_subs:
        a = data[i + 1] if i + 1 < len(data) else 0
        return 2, f'<40,{sub:02X}{a:02X}>'
    elif sub in two_arg_subs:
        a = data[i + 1] if i + 1 < len(data) else 0
        b = data[i + 2] if i + 2 < len(data) else 0
        return 3, f'<40,{sub:02X}{a:02X}{b:02X}>'
    elif sub in three_arg_subs:
        a = data[i + 1] if i + 1 < len(data) else 0
        b = data[i + 2] if i + 2 < len(data) else 0
        c = data[i + 3] if i + 3 < len(data) else 0
        return 4, f'<40,{sub:02X}{a:02X}{b:02X}{c:02X}>'
    else:
        print(f'  [WARNING] Unknown 0x40 sub-command: 0x{sub:02X}', file=sys.stderr)
        return 1, f'<40,{sub:02X}>'


def _decode_4A(data, i):
    if i + 1 >= len(data):
        return 0, '<4A>'
    arg = data[i]
    counter = data[i + 1]
    raw = data[i + 2:i + 2 + counter]
    hex_data = ''.join(f'{b:02x}' for b in raw)
    return 2 + counter, f'<4A,{arg:02x}{counter:02x}{hex_data}>\n'


# Map command bytes to their custom handler functions.
# Extend this dict to register additional dynamic handlers.
CUSTOM_HANDLERS = {
    0x40: _decode_40,
    0x4A: _decode_4A,
}


def decode_block(table, data):
    """
    Decode a block of bytes using Table for standard entries and
    CUSTOM_HANDLERS for bytes that require dynamic-length decoding.
    """
    parts = []
    i = 0
    while i < len(data):
        b = data[i]
        if b in CUSTOM_HANDLERS:
            consumed, text = CUSTOM_HANDLERS[b](data, i + 1)
            parts.append(text)
            i += 1 + consumed
        else:
            count, value = table._data_decode(table._table, data[i:])
            parts.append(str(value))
            i += count
    return ''.join(parts)


# ============================================================
# SNES ADDRESS → BANK ARRAY OFFSET (English Dialogue)
# ============================================================

def snes_to_bank_offset(snes_addr):
    if snes_addr < 0x238000:
        return snes_addr - 0x228000
    elif snes_addr < 0x248000:
        return snes_addr - 0x230000
    elif snes_addr < 0x258000:
        return snes_addr - 0x238000
    elif snes_addr < 0x268000:
        return snes_addr - 0x240000
    else:
        return snes_addr - 0x248000


# ============================================================
# POINTER TABLE READER
# ============================================================

def read_pointers(bank, region):
    bank_start = region['bank_start']
    ptr_table_start = region['ptr_table_start']
    ptr_table_end = region['ptr_table_end']
    section = region['section']

    pointers = []

    if section == 'dialogue':
        # 3-byte (24-bit SNES address) pointers
        ptr_count = (ptr_table_end - ptr_table_start - 2) // 3
        for i in range(ptr_count):
            offset = i * 3
            addr_in_bank = (ptr_table_start - bank_start) + offset
            lo  = bank[addr_in_bank]
            mid = bank[addr_in_bank + 1]
            hi  = bank[addr_in_bank + 2]
            value = lo + 0x100 * mid + 0x10000 * hi
            pointers.append((addr_in_bank, value))
    else:
        # 2-byte pointers; English menu values are direct bank array indices
        ptr_count = (ptr_table_end - ptr_table_start + 1) // 2
        for i in range(ptr_count):
            offset = i * 2
            addr_in_bank = (ptr_table_start - bank_start) + offset
            lo = bank[addr_in_bank]
            hi = bank[addr_in_bank + 1]
            value = lo + 256 * hi
            pointers.append((addr_in_bank, value))

    return pointers


# ============================================================
# DUMPER
# ============================================================

def rsaga_text_dumper(args):
    source_file = args.source_file
    table_file = args.table1
    dump_path = pathlib.Path(args.dump_path)
    table = Table(table_file)
    dump_path.mkdir(parents=True, exist_ok=True)

    with open(source_file, 'rb') as f:
        for mode, region in REGIONS.items():
            bank_start = region['bank_start']
            bank_read_size = region['bank_read_size']
            section = region['section']

            f.seek(bank_start)
            bank = bytearray(f.read(bank_read_size))

            pointers = read_pointers(bank, region)

            blocks = []
            if section == 'dialogue':
                for idx, (ptr_addr, snes_value) in enumerate(pointers):
                    start = snes_to_bank_offset(snes_value)
                    if idx < len(pointers) - 1:
                        stop = snes_to_bank_offset(pointers[idx + 1][1]) - 1
                    else:
                        stop = start + 1
                    blocks.append((idx, start, stop))
            else:
                for idx, (ptr_addr, value) in enumerate(pointers):
                    start = value
                    if idx < len(pointers) - 1:
                        stop = pointers[idx + 1][1] - 1
                    else:
                        try:
                            stop = bank.index(table.end_token[0], start)
                        except (ValueError, TypeError):
                            stop = len(bank) - 1
                    blocks.append((idx, start, stop))

            filename = dump_path / f'dump_{mode}.txt'
            with open(filename, 'w', encoding='utf-8') as out:
                for block_id, start, stop in blocks:
                    if start < 0 or start >= len(bank):
                        print(f'  [WARNING] Block {block_id}: start 0x{start:X} out of range', file=sys.stderr)
                        continue
                    block_bytes = bytes(bank[start:stop + 1])
                    text = decode_block(table, block_bytes)
                    out.write(f'>>>>>>>>>>\n')
                    out.write(f'Block {block_id}:\n')
                    out.write(f'{text}\n')

            print(f'{mode}: {len(blocks)} blocks written to {filename}')


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser('dump_text', help='Dump English text blocks to .txt files')
    sub.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Source ROM file')
    sub.add_argument('-t1', '--table1', action='store', dest='table1', help='TBL file')
    sub.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Output directory for dump files')
    sub.add_argument('-db', '--database', action='store', dest='database_file', help='Path to the SQLite database')
    sub.set_defaults(func=rsaga_text_dumper)

    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
