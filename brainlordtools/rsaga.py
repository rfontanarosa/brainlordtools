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
        # 2-byte pointers
        ptr_count = (ptr_table_end - ptr_table_start + 1) // 2
        for i in range(ptr_count):
            offset = i * 2
            addr_in_bank = (ptr_table_start - bank_start) + offset
            lo = bank[addr_in_bank]
            hi = bank[addr_in_bank + 1]
            # English menu: values are already bank array indices
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
                    text = table.decode(block_bytes)
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
