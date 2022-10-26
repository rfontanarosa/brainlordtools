__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3, shutil, csv
from collections import OrderedDict

from rhtools3.Table import Table
from rhutils.db import insert_text, select_translation_by_author, select_most_recent_translation
from rhutils.dump import read_text, write_text, write_byte, dump_binary, insert_binary, get_csv_translated_texts
from rhutils.rom import crc32
from rhutils.snes import snes2pc_lorom, pc2snes_lorom

CRC32 = 'C2ACD40D'

POINTER_BLOCKS = [
    (0x1867E, 0x18842, 0x10000),
    (0x1B54A, 0x1B74A, 0x10000),
    (0xC0000, 0xC01a0, 0xb8000),
    (0xC3CBE, 0xC3dc5, 0xb8000),
    (0x1D8000, 0x1D8014, 0x1D0000),
    (0x1D846A, 0x1D866A, 0x1D0000),
    (0x1DBF0A, 0x1DC106, 0x1D0000)
]

def ruinarm_read_text(f, offset):
    text = b''
    f.seek(offset)
    while True:
        Bytes = f.read(2)[::-1]
        if Bytes in (b'\xff\x00', b'\xff\x10',  b'\xff\x11',  b'\xff\x12', b'\xff\x13'):
            text += Bytes
            break
        elif Bytes == b'\xf0\x00':
            text += Bytes + f.read(2)[::-1]
            break
        else:
            text += Bytes
    return text

def ruinarm_text_dumper(args):
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
        for k, pointer_block in enumerate(POINTER_BLOCKS):
            # TEXT POINTERS
            pointers = OrderedDict()
            f.seek(pointer_block[0])
            while f.tell() < pointer_block[1]:
                p_address = f.tell()
                p_value = f.read(2)
                text_address = struct.unpack('H', p_value)[0] + pointer_block[2]
                pointers.setdefault(text_address, []).append(p_address)
            # TEXT
            for i, (text_address, p_addresses) in enumerate(pointers.items()):
                pointer_addresses = ';'.join(str(hex(x)) for x in p_addresses)
                text = ruinarm_read_text(f, text_address)
                text_decoded = table.decode(text)
                ref = '[BLOCK {}: {} to {} - BANK {} - {}]'.format(str(id), hex(text_address), hex(f.tell() -1), str(k + 1), pointer_addresses)
                # dump - db
                insert_text(cur, id, text, text_decoded, text_address, pointer_addresses, 1, ref)
                # dump - txt
                filename = os.path.join(dump_path, 'dump_jap.txt')
                with open(filename, 'a+') as out:
                    out.write(ref + '\n' + text_decoded + "\n\n")
                id += 1
        cur.close()
        conn.commit()
        conn.close()

def ruinarm_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table2_file = args.table2
    translation_path = args.translation_path
    db = args.database_file
    user_name = args.user
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table2_file)
    buffer = OrderedDict()
    #
    translation_file = os.path.join(translation_path, 'dump_ita.txt')
    with open(translation_file, 'r') as f:
        for line in f:
            if '[BLOCK ' in line:
                splitted_line = line.split(' ')
                block = int(splitted_line[1].replace(':', ''))
                offset_from = int(splitted_line[2], 16)
                offset_to = int(splitted_line[4], 16)
                buffer[block] = ['', [offset_from, offset_to]]
            else:
                buffer[block][0] += line
    #
    with open(dest_file, 'rb+') as f:
        for block, value in buffer.items():
            [text, offsets] = value
            encoded_text = table.encode(text[:-2])
            [offset_from, offset_to] = offsets
            f.seek(offset_from)

            swapped_text = b''
            i = 0
            while i < len(encoded_text):
                swapped_text += encoded_text[i:i+2][::-1]
                i += 2

            f.write(swapped_text)

            # if block == 3:
            #     print(swapped_text)
            #     print(table.decode(swapped_text, tbl_resolver=False, dict_resolver=False, mte_resolver=False, ctrl_resolver=False))
            #     print(hex(f.tell()))



import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=ruinarm_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=ruinarm_text_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
