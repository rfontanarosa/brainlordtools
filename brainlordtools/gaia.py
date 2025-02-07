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
from rhutils.snes import pc2snes_hirom, snes2pc_hirom

CRC32 = '1C3848C0'

EXP_SIZE = 0x80000

pointer_offsets_to_exclude = (0x5c94, 0x64e1c, 0xa0f3e, 0xaf75e, 0xdbdc, 0x11318, 0xd2ebc, 0x13321, 0x329b9, 0x80f93, 0xbe1ec, 0xba2dc, 0xba4f3, 0x80f93, 0xaedf9, 0xa468b, 0x226ab, 0x31732, 0xd3016, 0xdd242, 0xdd244, 0xdf92a, 0xe7728, 0xe7e76, 0xf3496, 0x1032df, 0x103c2a, 0x10d8c7, 0x118258, 0x12846b, 0x12b8f4, 0x13c9dd, 0x13f292, 0x14bd72, 0x151bc7, 0x1527eb, 0x15637d, 0x16c614, 0x16c61e, 0x171027, 0x184e15, 0x188d3b, 0x1909f0, 0x19853c, 0x1ddd09, 0x1e6886, 0x1ebcf8, 0x1edec7, 0x1f0973, 0x1f0b8b, 0x1f0bcb, 0x1f189b, 0x1f8cb2, 0x1f8e28, 0x1f9e90)

cmd_list = {b'\xc1': 2, b'\xc3': 1, b'\xc5': 4, b'\xc6': 4, b'\xc7': 2, b'\xc9': 1, b'\xcd': 3, b'\xd1': 2, b'\xd2': 1, b'\xd5': 1, b'\xd6': 1, b'\xd7': 1,}

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
            text = gaia_read_text(f, taddress, end_byte=(b'\xc0', b'\xca'), cmd_list=cmd_list, append_end_byte=True)
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

def gaia_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # Attacks
        filename = os.path.join(dump_path, 'attacks.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            for pointer_offset in tuple(range(0x8eb8f, 0x8eb9b, 2)) + tuple(range(0x1eba8, 0x1eda7, 2)) + tuple(range(0x1f54f, 0x1f6dc, 2)):
                f.seek(pointer_offset)
                pointer = f.read(2)
                bank_byte = pointer_offset & 0xFF0000
                taddress = pointer[0] + (pointer[1] << 8) + bank_byte
                text = gaia_read_text(f, taddress, end_byte=(b'\xc0', b'\xca'), cmd_list=cmd_list, append_end_byte=False)
                text_decoded = table.decode(text, mte_resolver=True, dict_resolver=True)
                fields = [hex(pointer_offset), text_decoded]
                csv_writer.writerow(fields)

def gaia_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table2_file = args.table2
    translation_path = args.translation_path
    db = args.database_file
    user_name = args.user
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table2_file)
    buffer = dict()
    #
    # conn = sqlite3.connect(db)
    # conn.text_factory = str
    # cur = conn.cursor()
    # rows = select_most_recent_translation(cur, ['1'])
    # for row in rows:
    #     _, _, text_decoded, _, _, translation, _, _, ref = row
    #     splitted_line = ref.split(' ')
    #     block = int(splitted_line[1].replace(':', ''))
    #     offset_from = int(splitted_line[2], 16)
    #     offset_to = int(splitted_line[4].replace(']', ''), 16)
    #     buffer[block] = ['', [offset_from, offset_to]]
    #     text = translation if translation else text_decoded
    #     buffer[block][0] = text + '\n\n'
    # cur.close()
    # conn.commit()
    # conn.close()
    #
    translation_file = os.path.join(translation_path, 'dump_ita.txt')
    with open(translation_file, 'r') as f:
        for line in f:
            if '[BLOCK ' in line:
                splitted_line = line.split(' ')
                block = int(splitted_line[1].replace(':', ''))
                offset_from = int(splitted_line[2], 16)
                offset_to = int(splitted_line[4].replace(']\n', ''), 16)
                buffer[block] = ['', [offset_from, offset_to]]
            else:
                buffer[block][0] += line
    with open(dest_file, 'rb+') as f:
        total = 0
        offsets_list = []
        new_offset = 0x208_000
        f.seek(new_offset)
        for block, value in buffer.items():
            text, offsets = value
            original_text_offset, _ = offsets
            if block in (1165,):
                continue
            encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
            total += len(encoded_text)
            if len(encoded_text) < 5:
                continue
            if f.tell() + len(encoded_text) > new_offset + 0x8_000:
                new_offset += 0x10_000
                f.seek(new_offset)
            offsets_list.append((original_text_offset, f.tell(), encoded_text[-1]))
            f.write(encoded_text[:-1] + b'\xca')
        for id, offsets in enumerate(offsets_list):
            if id + 1 in (1165,):
                continue
            original_text_offset, new_text_offset, end_byte = offsets
            snes_offset = pc2snes_hirom(new_text_offset) - 0x400_000
            new_pointer = struct.pack('<I', snes_offset)
            f.seek(original_text_offset)
            f.write(b'\xcd' + new_pointer[:3] + bytes([end_byte]))

def gaia_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, 0x258_000, 0x258_000 + 4314, translation_path, 'font_ita.bin')
        f.seek(0xd8008)
        snes_offset = pc2snes_hirom(0x258_000) - 0x400_000
        new_pointer = struct.pack('<I', snes_offset)
        f.write(new_pointer[:3])

def gaia_expander(args):
    dest_file = args.dest_file
    expand_rom(dest_file, EXP_SIZE)

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
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=gaia_text_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=gaia_misc_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=gaia_gfx_inserter)
expand_parser = subparsers.add_parser('expand', help='Execute EXPANDER')
expand_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
expand_parser.set_defaults(func=gaia_expander)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
