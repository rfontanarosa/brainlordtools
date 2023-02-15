__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, struct, sys


from rhutils.dump import read_text, write_text, dump_binary, insert_binary, get_csv_translated_texts
from rhutils.rom import crc32, expand_rom
from rhutils.table import Table

CRC32 = '1C3848C0'

TEXT_POINTERS = (0x16000, 0x16112)
MISC_POINTERS1 = (0x16114, 0x16122)
MISC_POINTERS2 = (0x16128, 0x16208)
# MISC_POINTERS3 = (0xff73, 0xff82)
# MISC_POINTERS = (0xfd74, )

def gargoyle_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        id = 1
        start, end = TEXT_POINTERS
        # READ POINTERS BLOCK
        pointers = {}
        f.seek(start)
        while f.tell() <= end:
            p_offset = f.tell()
            p_value = struct.unpack('H', f.read(2))[0] + 0x10000
            print(hex(p_value))
            # sys.exit()
            pointers.setdefault(p_value, []).append(p_offset)
        # READ TEXT BLOCK
        for _, (taddress, paddresses) in enumerate(pointers.items()):
            pointer_addresses = ';'.join(hex(x) for x in paddresses)
            text = read_text(f, taddress, end_byte=b'\x7f')
            text_decoded = table.decode(text)
            ref = f'[ID {id} - TEXT {hex(taddress)} - POINTER {pointer_addresses}]'
            # dump - txt
            filename = os.path.join(dump_path, 'dump_eng.txt')
            with open(filename, 'a+', encoding='utf-8') as out:
                out.write(f'{ref}\n{text_decoded}\n\n')
            id += 1

def gargoyle_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    table2_file = args.table2
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    table2 = Table(table2_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        #
        filename = os.path.join(dump_path, 'misc1.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
            pointers = {}
            f.seek(MISC_POINTERS1[0])
            while f.tell() < MISC_POINTERS1[1]:
                pointers[f.tell()] = struct.unpack('H', f.read(2))[0] + 0x10000
            for pointer, value in pointers.items():
                f.seek(value)
                text = read_text(f, f.tell(), end_byte=b'\x75')
                text_decoded = table.decode(text)
                fields = [hex(pointer), hex(value), text_decoded]
                csv_writer.writerow(fields)
        #
        filename = os.path.join(dump_path, 'misc2.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
            pointers = {}
            f.seek(MISC_POINTERS2[0])
            while f.tell() < MISC_POINTERS2[1]:
                pointers[f.tell()] = struct.unpack('H', f.read(2))[0] + 0x10000
            for pointer, value in pointers.items():
                f.seek(value)
                text = read_text(f, f.tell(), end_byte=b'\x00')
                text_decoded = table.decode(text)
                fields = [hex(pointer), hex(value), text_decoded]
                csv_writer.writerow(fields)

def gargoyle_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table2_file = args.table2
    translation_path = args.translation_path
    db = args.database_file
    user_name = args.user
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table2_file)
    buffer = {}

    translation_file = os.path.join(translation_path, 'dump_eng.txt')
    with open(translation_file, 'r') as f:
        for line in f:
            if '[ID ' in line:
                splitted_line = line.split(' ')
                block = int(splitted_line[1].replace(':', ''))
                # offset_from = int(splitted_line[2], 16)
                # offset_to = int(splitted_line[4].replace(']\n', ''), 16)
                # buffer[block] = ['', [offset_from, offset_to]]
                buffer[block] = ['']
            else:
                buffer[block][0] += line

    translation = b''
    for _, value in buffer.items():
        [text] = value
        translation += table.encode(text)
    print(len(translation))

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.set_defaults(func=gargoyle_text_dumper)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMPER')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=gargoyle_misc_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=gargoyle_text_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
