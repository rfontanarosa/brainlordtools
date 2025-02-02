__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, re, shutil, sqlite3, struct, sys

from rhtools3.Table import Table
from rhutils.db import insert_text, select_translation_by_author, select_most_recent_translation
from rhutils.dump import write_text, dump_binary, insert_binary, get_csv_translated_texts
from rhutils.rom import crc32, expand_rom
from rhutils.snes import snes2pc_hirom

CRC32 = '1C3848C0'

pointer_offsets_to_exclude = (0x5c94, 0x64e1c, 0xa0f3e, 0xaf75e, 0xdbdc, 0x11318, 0xd2ebc, 0x13321, 0x329b9, 0x80f93, 0xbe1ec, 0xba2dc, 0xba4f3, 0x80f93, 0xaedf9, 0xa468b, 0x226ab, 0x31732, 0xd3016, 0xdd242, 0xdd244, 0xdf92a, 0xe7728, 0xe7e76, 0xf3496, 0x1032df, 0x103c2a, 0x10d8c7, 0x118258, 0x12846b, 0x12b8f4, 0x13c9dd, 0x13f292, 0x14bd72, 0x151bc7, 0x1527eb, 0x15637d, 0x16c614, 0x16c61e, 0x171027, 0x184e15, 0x188d3b, 0x1909f0, 0x19853c, 0x1ddd09, 0x1e6886, 0x1ebcf8, 0x1edec7, 0x1f0973, 0x1f0b8b, 0x1f0bcb, 0x1f189b, 0x1f8cb2, 0x1f8e28, 0x1f9e90)

def gaia_read_text(f, offset=None, length=None, end_byte=None, cmd_list=None, append_end_byte=False):
    text = b''
    if offset is not None:
        f.seek(offset)
    if length:
        text = f.read(length)
    elif end_byte:
        while True:
            byte = f.read(1)
            if cmd_list and byte in cmd_list.keys():
                bytes_to_read = cmd_list.get(byte)
                read_bytes = f.read(bytes_to_read)
                if byte == b'\xd1':
                    bank_byte = f.tell() & 0xFF0000
                    offset = read_bytes[0] + (read_bytes[1] << 8) + bank_byte
                    f.seek(offset)
                elif byte == b'\xcd':
                    offset_snes = (read_bytes[2] << 16) | (read_bytes[1] << 8) | read_bytes[0]
                    offset_pc = snes2pc_hirom(offset_snes)
                    current_offset = f.tell()
                    text += gaia_read_text(f, offset=offset_pc, end_byte=end_byte, cmd_list=cmd_list)
                    f.seek(current_offset)
                else:
                    text += byte + read_bytes
            elif byte in end_byte:
                if append_end_byte:
                    text += byte
                break
            else:
                text += byte
    return text

def gaia_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    db = args.database_file
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        id = 1
        pointers = {}
        pointer_offsets = [m.start() for m in re.finditer(b'\x02\xbf', f.read())]
        for pointer_offset in pointer_offsets:
            if pointer_offset in pointer_offsets_to_exclude:
                continue
            f.seek(pointer_offset)
            pointer = f.read(4)[2:]
            bank_byte = pointer_offset & 0xFF0000
            taddress = pointer[0] + (pointer[1] << 8) + bank_byte
            pointers.setdefault(taddress, []).append(pointer_offset)
        for i, (taddress, paddresses) in enumerate(pointers.items()):
            text = gaia_read_text(f, taddress, end_byte=(b'\xc0', b'\xca'), cmd_list={b'\xc1': 2, b'\xc3': 1, b'\xc5': 4, b'\xc6': 4, b'\xc7': 2, b'\xc9': 1, b'\xcd': 3, b'\xd1': 2, b'\xd2': 1, b'\xd5': 1, b'\xd6': 1, b'\xd7': 1,}, append_end_byte=True)
            text_decoded = table.decode(text, mte_resolver=True, dict_resolver=True)
            pointer_addresses = ';'.join(hex(x) for x in paddresses)
            ref = f'[BLOCK {id}: {hex(taddress)} to {hex(f.tell() - 1)} - {pointer_addresses}]'
            # dump - db
            # insert_text(cur, id, text, text_decoded, text_address, '', 1, ref)
            # dump - txt
            filename = os.path.join(dump_path, 'dump_eng.txt')
            with open(filename, 'a+', encoding='utf-8') as out:
                out.write(f'{ref}\n{text_decoded}\n\n')
            id += 1
    cur.close()
    conn.commit()
    conn.close()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=gaia_text_dumper)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
