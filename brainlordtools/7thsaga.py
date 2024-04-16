__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3, shutil, csv

from rhtools3.Table import Table
from rhutils.db import insert_text, select_translation_by_author, select_most_recent_translation
from rhutils.dump import read_text, write_text, dump_binary, insert_binary
from rhutils.rom import crc32
from rhutils.snes import snes2pc_lorom, pc2snes_lorom

# ORIGINAL
# CRC32 = 'B3ABDDE6'

# UNPACKED GFX
CRC32 = '2979C59'

TEXT_BLOCK1 = (0x60000, 0x6fdde)
TEXT_BLOCK2 = (0x70000, 0x733c1)
TEXT_BLOCK3 = (0x741f7, 0x75343)

MISC_BLOCK1 = (0x733c2, 0x741f6)
MISC_BLOCK2 = (0x75345, 0x7545f)

POINTER_BLOCKS = [(0x1a0ad, 0x1a0c1), (0x425db, 0x4269a)]

FONT1_BLOCK = (0x13722d, 0x13B22d)

def dump_blocks(f, table, dump_path):
    filename = os.path.join(dump_path, 'misc1.csv')
    with open(filename, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(MISC_BLOCK1[0])
        while f.tell() <= MISC_BLOCK1[1]:
            text_address = f.tell()
            text = read_text(f, text_address, end_byte=b'\xf7')
            text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
            fields = [hex(text_address), text_decoded]
            csv_writer.writerow(fields)
    filename = os.path.join(dump_path, 'misc2.csv')
    with open(filename, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(MISC_BLOCK2[0])
        while f.tell() <= MISC_BLOCK2[1]:
            text_address = f.tell()
            text = read_text(f, text_address, end_byte=b'\xf7')
            text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
            fields = [hex(text_address), text_decoded]
            csv_writer.writerow(fields)

def get_pointers(f, start, count, step):
    pointers = {}
    end = start + (count * step)
    f.seek(start)
    while f.tell() < end:
        p_offset = f.tell()
        pointer = f.read(step)
        p_value = struct.unpack('i', pointer[:3] + b'\x00')[0] - 0xc00000
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_translated_texts(filename):
    translated_texts = {}
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            text_address = int(row['text_address'], 16)
            translated_texts[text_address] = trans
    return translated_texts

def repoint_misc(f, pointers, new_pointers, table=None):
    for i, (p_value, p_addresses) in enumerate(pointers.items()):
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print('repoint_misc - Text not found - Text offset: ' + hex(p_value))
        else:
            a = f.tell()
            text = read_text(f, p_new_value, end_byte=b'\xf7')
            t2 = table.decode(text, mte_resolver=True, dict_resolver=False)
            print(f'repoint_misc - {t2} - Text offset: {hex(p_value)}' + ' - Pointer offset: ' + hex(f.tell()))
            f.seek(p_new_value)
            f.seek(a)
            for p_address in p_addresses:
                f.seek(p_address)
                packed = struct.pack('i', p_new_value + 0xc00000)
                f.write(packed[:-1])

def seventhsaga_text_segment_dumper(f, dump_path, table, id, block, cur, start=0x0, end=0x0):
    f.seek(start)
    while f.tell() < end:
        text_address = f.tell()
        text = read_text(f, text_address, end_byte=b'\xf7', cmd_list={b'\xfc': 5})
        text_decoded = table.decode(text, mte_resolver=True, dict_resolver=False, cmd_list={0xf6: 1, 0xfb: 5, 0xfc: 5, 0xfd: 2, 0xfe: 2, 0xff: 3})
        ref = '[BLOCK {}: {} to {}]'.format(str(id), hex(text_address), hex(f.tell()))
        # dump - db
        insert_text(cur, id, text, text_decoded, text_address, '', block, '')
        # dump - txt
        filename = os.path.join(dump_path, 'dump_eng.txt')
        with open(filename, 'a+') as out:
            out.write(ref + '\n' + text_decoded + "\n\n")
        id += 1
    return id

def seventhsaga_text_dumper(args):
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
        id = seventhsaga_text_segment_dumper(f, dump_path, table, id, 1, cur, TEXT_SEGMENT_1[0], TEXT_SEGMENT_1[1])
        id = seventhsaga_text_segment_dumper(f, dump_path, table, id, 2, cur, TEXT_SEGMENT_2[0], TEXT_SEGMENT_2[1])
        id = seventhsaga_text_segment_dumper(f, dump_path, table, id, 3, cur, TEXT_SEGMENT_3[0], TEXT_SEGMENT_3[1])
    cur.close()
    conn.commit()
    conn.close()

def seventhsaga_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table2_file = args.table2
    translation_path = args.translation_path
    db = args.database_file
    user_name = args.user
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table2_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    # collect pointers
    NEW_TEXT_BLOCK1_START = NEW_TEXT_BLOCK1_END = 0x300000
    new_pointers = {}
    with open(dest_file, 'r+b') as fw:
        fw.seek(NEW_TEXT_BLOCK1_START)
        # db
        rows = select_most_recent_translation(cur, ['1', '2', '3'])
        for row in rows:
            _, _, text_decoded, address, _, translation, _, _, _ = row
            text = translation if translation else text_decoded
            encoded_text = table.encode(text, mte_resolver=True, dict_resolver=False)
            if fw.tell() < 0x310000 and fw.tell() + len(encoded_text) > 0x30ffff:
                fw.seek(0x310000)
            new_pointers[int(address)] = fw.tell()
            fw.write(encoded_text)
            fw.write(b'\xf7')
        NEW_TEXT_BLOCK1_END = fw.tell()
    # find pointers
    address = 0x626ca
    if address:
        pointer = new_pointers.get(address)
        with open(dest_file, 'r+b') as fw:
            file = fw.read()
            packed = struct.pack('i', address + 0xc00000)[:-1]
            print(packed)
            print(hex(pointer))
            offsets = [i for i in range(len(file)) if file.startswith(packed, i)]
            hex_offsets = list(map(lambda x: hex(x), offsets))
            print(hex_offsets)
    # pointer block 1
    with open(dest_file, 'r+b') as fw:
        for POINTER_BLOCK in POINTER_BLOCKS:
            fw.seek(POINTER_BLOCK[0])
            while (fw.tell() < POINTER_BLOCK[1]):
                repoint_text(fw, fw.tell(), new_pointers)
    # text block pointers
    with open(dest_file, 'r+b') as fw:
        fw.seek(NEW_TEXT_BLOCK1_START)
        while (fw.tell() < NEW_TEXT_BLOCK1_END):
            byte = fw.read(1)
            if byte in (b'\xfb', b'\xfc'):
                fw.read(2)
                repoint_text(fw, fw.tell(), new_pointers)
            elif byte == b'\xff':
                repoint_text(fw, fw.tell(), new_pointers)
    # sparse pointers
    with open(dest_file, 'r+b') as fw:
        sparse_pointers = (0x56f0a, 0x56f10, 0x56f16, 0x56f1c, 0x56f22, 0x56f28)
        sparse_pointers = sparse_pointers + (0x56f88, 0x56f8e, 0x56f94, 0x56f9a, 0x56fa0, 0x56fa6, 0x56fac, 0x56fb2, 0x56fb8)
        sparse_pointers = sparse_pointers + (0x57012, 0x57018, 0x5701e, 0x57024, 0x5702a)
        sparse_pointers = sparse_pointers + (0x57090, 0x57096, 0x5709c, 0x570a2, 0x570a8)
        sparse_pointers = sparse_pointers + (0x57114, 0x5711a, 0x57120, 0x57126, 0x5712c, 0x57132, 0x57138, 0x5713e, 0x57144, 0x57192, 0x57198)
        sparse_pointers = sparse_pointers + (0x158fd5, 0x158fe7, 0x158fff, 0x15901d, 0x159035, 0x15903b, 0x15905f, 0x159065, 0x15906b, 0x1590bf, 0x1590c5, 0x1590d7, 0x1590f5, 0x159131, 0x159149, 0x15914f, 0x159185, 0x15918b, 0x15919d, 0x1591af, 0x1591c1, 0x1591d3, 0x1591d9, 0x1591eb, 0x1591f1)
        sparse_pointers = sparse_pointers + (0x15920f, 0x159215, 0x15921b, 0x15924b, 0x159251, 0x159269, 0x159281, 0x159287, 0x15928d, 0x15929f, 0x1592a5, 0x1592b7, 0x1592bd, 0x1592c3, 0x1592c9, 0x1592cf, 0x1592e1, 0x1592e7, 0x1592ed, 0x1592f3, 0x1592f9, 0x1592ff)
        sparse_pointers = sparse_pointers + (0x159347, 0x15934d, 0x15936b, 0x159371, 0x159389, 0x159395, 0x1593cb, 0x1593e9, 0x1593ef)
        sparse_pointers = sparse_pointers + (0x15940d, 0x159413, 0x159419, 0x15941f, 0x159455,0x159485, 0x159497, 0x15949d)
        sparse_pointers = sparse_pointers + (0x159515, 0x159629, 0x1596fb, 0x159737, 0x1598d5, 0x159a13, 0x159bbd, 0x159deb, 0x15a151, 0x15a2ad, 0x15a59b, 0x15a89b, 0x15ab8f, 0x15ac0d, 0x15af1f, 0x15af61, 0x15b057, 0x15b11d, 0x15b25b, 0x15b453, 0x15baa7, 0x15bafb, 0x15bc21, 0x15d0f1)
        sparse_pointers = sparse_pointers + (0x159017, 0x159233, 0x159329) # Welcome to our store! (0x60003)
        sparse_pointers = sparse_pointers + (0x159167, 0x15926f, 0x15938f, 0x15943d, 0x1595f9, 0x159791, 0x159881, 0x1599f5) # Hello! I sell armor. (0x6005a)
        sparse_pointers = sparse_pointers + (0x15d57d,)
        for sparse_pointer in sparse_pointers:
            repoint_text(fw, sparse_pointer, new_pointers)
    # # two bytes pointers
    with open(dest_file, 'r+b') as fw:
        repoint_two_bytes_pointer(fw, 0x8eb2, new_pointers, b'\xc6') # 0x604a7 # What else would you like?
        repoint_two_bytes_pointer(fw, 0xa0b7, new_pointers, b'\xc6') # 0x604a7 # What else would you like?
        repoint_two_bytes_pointer(fw, 0xaafb, new_pointers, b'\xc6') # 0x604a7 # What else would you like?
        repoint_two_bytes_pointer(fw, 0x8f9b, new_pointers, b'\xc6') # 0x604bc # Thank you. Come back again.
        repoint_two_bytes_pointer(fw, 0xa1a0, new_pointers, b'\xc6') # 0x604bc # Thank you. Come back again.
        repoint_two_bytes_pointer(fw, 0xac1c, new_pointers, b'\xc6') # 0x604bc # Thank you. Come back again.
        repoint_two_bytes_pointer(fw, 0x9134, new_pointers, b'\xc6') # 0x600e1 # Which would you like?
        repoint_two_bytes_pointer(fw, 0xa339, new_pointers, b'\xc6') # 0x600e1 # Which would you like?
        repoint_two_bytes_pointer(fw, 0xb1d1, new_pointers, b'\xc6') # 0x600e1 # Which would you like?
        repoint_two_bytes_pointer(fw, 0x9962, new_pointers, b'\xc6') # 0x60762 # Do you need any other help?
        repoint_two_bytes_pointer(fw, 0x9a44, new_pointers, b'\xc6') # 0x60776 # Come back anytime you need my help.
        repoint_two_bytes_pointer(fw, 0x9b99, new_pointers, b'\xc6') # 0x6079f # You don't need the service.
        repoint_two_bytes_pointer(fw, 0x9e7d, new_pointers, b'\xc6') # 0x6079f # You don't need the service.
        repoint_two_bytes_pointer(fw, 0xad25, new_pointers, b'\xc6') # 0x60247 # What would you like to sell?
        repoint_two_bytes_pointer(fw, 0xb097, new_pointers, b'\xc6') # 0x60294 # I will buy
        repoint_two_bytes_pointer(fw, 0xb42a, new_pointers, b'\xc6') # 0x60277 # I will buy
        repoint_two_bytes_pointer(fw, 0xb5a5, new_pointers, b'\xc6') # 0x6058b # Welcome to my Inn!
        repoint_two_bytes_pointer(fw, 0x668, new_pointers, b'\xc6') # 0x6085e # Intro 1
        repoint_two_bytes_pointer(fw, 0x7d8, new_pointers, b'\xc6') # 0x60 # Intro 2
        repoint_two_bytes_pointer(fw, 0x8d3, new_pointers, b'\xc6') # 0x60 # Intro 3
        repoint_two_bytes_pointer(fw, 0xa39, new_pointers, b'\xc6') # 0x60 # Intro 4
        repoint_two_bytes_pointer(fw, 0xb34, new_pointers, b'\xc6') # 0x60 # Intro 5
    cur.close()
    conn.commit()
    conn.close()

def seventhsaga_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[1], dump_path, 'gfx_font1.bin')

def seventhsaga_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[1], translation_path, 'gfx_font1.bin')

def seventhsaga_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_blocks(f, table, dump_path)

def seventhsaga_misc_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    table2_file = args.table2
    translation_path = args.translation_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    table2 = Table(table2_file)
    # get pointers
    with open(source_file, 'rb') as f:
        # get misc1 pointers
        pointers_1_1 = get_pointers(f, 0x8320, 38, 27) # Lemele...
        pointers_1_2 = get_pointers(f, 0x8209, 7, 42)  # Guanta...
        pointers_1_3 = get_pointers(f, 0x6c9a, 99, 9)  # Exigate, Watr Rn, Potn [1], MHerb [1]...
        pointers_1_4 = get_pointers(f, 0x7015, 61, 12) # FIRE [1]
        pointers_1_5 = get_pointers(f, 0x45f1c, 7, 3)  # Town menu
        pointers_1_6 = get_pointers(f, 0x45f46, 7, 3)  # Map menu
        pointers_1_7 = get_pointers(f, 0x45f70, 7, 3)  # Battle menu
    # repoint text
    with open(dest_file, 'r+b') as f1:
        # reading misc1.csv and writing texts
        translation_file = os.path.join(translation_path, 'misc1.csv')
        translated_texts = get_translated_texts(translation_file)
        new_pointers = {}
        t_new_address = 0x350000
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            new_pointers[t_address] = t_new_address
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            t_new_address = write_text(f1, t_new_address, text, end_byte=b'\xf7')
        # repointing misc1
        for curr_pointers in (pointers_1_1, pointers_1_2, pointers_1_3, pointers_1_4, pointers_1_5, pointers_1_6, pointers_1_7):
            repoint_misc(f1, curr_pointers, new_pointers, table)

def repoint_two_bytes_pointer(fw, offset, new_pointers, third_byte):
    fw.seek(offset)
    pointer = fw.read(2)
    unpacked = struct.unpack('i', pointer + third_byte + b'\x00')[0] - 0xc00000
    new_pointer = new_pointers.get(unpacked)
    if new_pointer:
        fw.seek(-2, os.SEEK_CUR)
        packed = struct.pack('i', new_pointer + 0xc00000)
        fw.write(packed[:-2])
        fw.seek(5, os.SEEK_CUR)
        fw.write(packed[2:3])
    else:
        print(f'CHOICE - Pointer offset: {hex(offset)} - Pointer value: {hex(unpacked)}')

def repoint_text(fw, offset, new_pointers):
    fw.seek(offset)
    pointer = fw.read(3)
    unpacked = struct.unpack('i', pointer + b'\x00')[0] - 0xc00000
    new_pointer = new_pointers.get(unpacked)
    if new_pointer:
        fw.seek(-3, os.SEEK_CUR)
        packed = struct.pack('i', new_pointer + 0xc00000)
        fw.write(packed[:-1])
    else:
        if unpacked == 0x173419:
            fw.seek(-3, os.SEEK_CUR)
            packed = struct.pack('i', fw.tell() + 3 + 0xc00000)
            fw.write(packed[:-1])
        else:
            print(f'TEXT - Pointer offset: {hex(offset)} - Pointer value: {hex(unpacked)}')

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
dump_text_parser.set_defaults(func=seventhsaga_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=seventhsaga_text_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=seventhsaga_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=seventhsaga_gfx_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=seventhsaga_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=seventhsaga_misc_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
