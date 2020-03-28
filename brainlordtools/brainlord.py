# -*- coding: utf-8 -*-

__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3, shutil, csv
from collections import OrderedDict

from rhtools.utils import crc32, byte2int, int2byte, int2hex
from rhtools.Table import Table

CRC32 = 'AC443D87'

TEXT_BLOCK1_START = 0x170000
TEXT_BLOCK1_END = 0x17fac9
#TEXT_BLOCK1_LIMIT = 0x17ffff

TEXT_BLOCK2_START = 0x8dec1
TEXT_BLOCK2_END = 0x8f9ed
#TEXT_BLOCK2_LIMIT = 0x903ff

POINTER_BLOCK1_START = 0x50013
POINTER_BLOCK1_END = 0x50267

ITEM_POINTERS_START = 0x18a02
ITEM_POINTERS_END = 0x19388

TEXT_BLOCK = OrderedDict()
TEXT_BLOCK['misc'] = (0x67104, 0x67768)

FONT1_BLOCK = (0x74000, 0x78000)
FONT2_BLOCK = (0x80000, 0x82000)

def read_text(f, end_byte=0xf7):
    text = b''
    byte = b'1'
    while not byte2int(byte) == end_byte:
        byte = f.read(1)
        if byte2int(byte) != end_byte:
            text += byte
    return text

def decode_text(text):
    return text

def write_text(f, offset, text, table, end_byte=0xf7, limit=None):
    f.seek(offset)
    text = decode_text(text)
    decoded_text = table.decode(text, mte_resolver=False, dict_resolver=False)
    f.write(decoded_text)
    f.write(int2byte(end_byte))
    if limit and f.tell() > limit:
        raise Exception()
    return f.tell()

def dump_blocks(f, table, dump_path):
    filename = os.path.join(dump_path, 'misc1.csv')
    with open(filename, 'wb+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(0x67104)
        while f.tell() < 0x67768:
            text_address = f.tell()
            text = read_text(f)
            text_encoded = table.encode(text, mte_resolver=True, dict_resolver=False)
            fields = [int2hex(text_address), text_encoded]
            csv_writer.writerow(fields)
    filename = os.path.join(dump_path, 'misc2.csv')
    with open(filename, 'wb+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(0x12030d)
        while f.tell() < 0x1208ac:
            text_address = f.tell()
            text = read_text(f)
            text_encoded = table.encode(text, mte_resolver=True, dict_resolver=False)
            fields = [int2hex(text_address), text_encoded]
            csv_writer.writerow(fields)

def dump_gfx(f, start, end, dump_path, filename):
    f.seek(start)
    block_size = end - start
    block = f.read(block_size)
    with open(os.path.join(dump_path, filename), 'wb') as gfx_file:
        gfx_file.write(block)

def insert_gfx(f, start, end, translation_path, filename):
    with open(os.path.join(translation_path, filename), 'rb') as f1:
        block = f1.read()
        if len(block) == end - start:
            f.seek(start)
            f.write(block)
        else:
            raise Exception('GFX file - Different size')

def get_pointers(f, start, end, step):
    pointers = OrderedDict()
    f.seek(start)
    while(f.tell() < end):
        p_offset = f.tell()
        pointer = f.read(step)
        p_value = struct.unpack('i', pointer[:3] + '\x00')[0] - 0xc00000
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_translated_texts(filename):
    translated_texts = OrderedDict()
    with open(filename, 'rb') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            trans = trans.decode('utf-8')
            text_address = int(row['text_address'], 16)
            translated_texts[text_address] = trans
    return translated_texts

def repoint_misc(f, pointers, new_pointers):
    for p_value, p_addresses in pointers.iteritems():
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print('Misc not found! ' + int2hex(p_value))
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                packed = struct.pack('i', p_new_value + 0xc00000)
                f.write(packed[:-1])

def brainlord_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_blocks(f, table, dump_path)

def brainlord_misc_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    translation_path = args.translation_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    with open(source_file, 'rb') as f0:
        p_a1 = get_pointers(f0, 0x18a0f, 0x18a0f + (40 * 13), 13)
        p_a2 = get_pointers(f0, 0x18c17, 0x18c17 + (64 * 10), 10)
        p_a3 = get_pointers(f0, 0x18e97, 0x18e97 + (41 * 13), 13)
        p_a4 = get_pointers(f0, 0x1909f, 0x1909f + (81 * 10), 10)
        p_a5 = get_pointers(f0, 0x193c9, 0x193d5 + (30 * 12), 12)
        p_b1 = get_pointers(f0, 0x16f54, 0x16f54 + (16 * 18), 18) #Remeer... Jima
        p_b2 = get_pointers(f0, 0x17210, 0x17210 + (16 * 7), 7) #Ason...
        p_b3 = get_pointers(f0, 0x65b7e, 0x65b7e + (65 * 6), 6) #Arcs...
        p_b4 = get_pointers(f0, 0x60658, 0x60658 + (12 * 3), 3) #Morguai...
        p_b5 = get_pointers(f0, 0x164b, 0x164b + (5 * 3), 3) #Items, Magic, Config., Status, Return
        p_b6 = get_pointers(f0, 0x1980, 0x1980 + (2 * 3), 3) #Message, Key
        p_b7 = get_pointers(f0, 0x1b57, 0x1b57 + (3 * 3), 3) #Attack......, Jump........, Defense.....
        p_b8 = get_pointers(f0, 0x2232d, 0x2232d + (4 * 3), 3) #Buy, Trade, Sell, Quit
        p_b9 = get_pointers(f0, 0x2353b, 0x2353b + (3 * 3), 3) #Buy, Sell, Quit
        p_b10 = get_pointers(f0, 0x23edb, 0x23edb + (2 * 3), 3) #Buy, Quit
        p_b11 = get_pointers(f0, 0x24491, 0x24491 + (3 * 3), 3) #Buy, Sell, Quit
        p_b12 = get_pointers(f0, 0x140860, 0x140860 + (2 * 3), 3) #Continue, Erase
        p_b13 = get_pointers(f0, 0x14086a, 0x14086a + (1 * 3), 3) #Beginning
        p_b14 = get_pointers(f0, 0x140871, 0x140871 + (4 * 3), 3) #Continue, Beginning, Erase, Copy
        p_b15 = get_pointers(f0, 0x1ead, 0x1ead + (3 * 3), 3) #Fast, Normal, Slow
        p_b16 = get_pointers(f0, 0x1b63, 0x1b63 + (2 * 3), 3) #Enter Com. , Cancel Com. 
        p_b17 = get_pointers(f0, 0x140a51, 0x140a51 + (3 * 2), 3) #Erase, Quit
        p_b18 = get_pointers(f0, 0x140ca6, 0x140ca6 + (3 * 2), 3) #Copy, Quit
        p_b19 = get_pointers(f0, 0x2950, 0x2950 + (3 * 3), 3) #Equ., Copy, Dis.
        p_b20 = get_pointers(f0, 0x295d, 0x295d + (3 * 3), 3) #Use, Copy, Dis.
        p_b21 = get_pointers(f0, 0x22f6, 0x22f6 + (3 * 4), 3) #LV, Power, Ex,  ^
        p_b22 = get_pointers(f0, 0x1ddbc, 0x1ddbc + (3 * 11), 3) #Warp, Escape, Flag, Items, Level, Slow, Time, Set, Task, Sound, Memory
        p_b23 = get_pointers(f0, 0x2c92f, 0x2c92f + (3 * 2), 3) #Yes, No
        """
        for text_offset in (p_b23):
            f0.seek(text_offset)
            text = read_text(f0)
            decoded_text = table.encode(text, mte_resolver=True, dict_resolver=False)
            print int2hex(text_offset)
            print decoded_text
        """
    with open(dest_file, 'r+b') as f1:
        """ misc1.csv """
        translation_file = os.path.join(translation_path, 'misc1.csv')
        translated_texts = get_translated_texts(translation_file)
        new_pointers = OrderedDict()
        t_new_address = 0x180000
        for t_address, t_value in translated_texts.iteritems():
            new_pointers[t_address] = t_new_address
            t_new_address = write_text(f1, t_new_address, t_value, table)
        # repointing
        for curr_pointers in (p_a1, p_a2, p_a3, p_a4, p_a5):
            repoint_misc(f1, curr_pointers, new_pointers)
        """ misc2.csv """
        translation_file = os.path.join(translation_path, 'misc2.csv')
        translated_texts = get_translated_texts(translation_file)
        new_pointers = OrderedDict()
        t_new_address = 0x182000
        for t_address, t_value in translated_texts.iteritems():
            new_pointers[t_address] = t_new_address
            t_new_address = write_text(f1, t_new_address, t_value, table)
        # repointing
        for curr_pointers in (p_b1, p_b2, p_b3, p_b4, p_b5, p_b6, p_b7, p_b8, p_b9, p_b10, p_b11, p_b12, p_b13, p_b14, p_b15, p_b16, p_b17, p_b18, p_b19, p_b20, p_b21, p_b22, p_b23):
            repoint_misc(f1, curr_pointers, new_pointers)

def brainlord_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_gfx(f, FONT1_BLOCK[0], FONT1_BLOCK[1], dump_path, 'gfx_font1.bin')
        dump_gfx(f, FONT2_BLOCK[0], FONT2_BLOCK[1], dump_path, 'gfx_font2.bin')

def brainlord_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_gfx(f, FONT1_BLOCK[0], FONT1_BLOCK[1], translation_path, 'gfx_font1.bin')
        insert_gfx(f, FONT2_BLOCK[0], FONT2_BLOCK[1], translation_path, 'gfx_font2.bin')

def brainlord_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    db = args.database_file
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        id = 1
        f.seek(TEXT_BLOCK1_START)
        while f.tell() < TEXT_BLOCK1_END:
            text_address = f.tell()
            text = read_text(f)
            text_encoded = table.encode(text, mte_resolver=True, dict_resolver=False, cmd_list=[(0xf6, 1), (0xfb, 5), (0xfc, 5), (0xfd, 2), (0xfe, 2), (0xff, 3)])
            # dump - db
            text_binary = sqlite3.Binary(text)
            text_length = len(text_binary)
            cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, 1)', (id, buffer(text_binary), text_encoded, text_address, '', text_length))
            # dump - txt
            filename = os.path.join(dump_path, '%s - %d.txt' % (str(id).zfill(3), text_address))
            with open(filename, 'w') as out:
                out.write(text_encoded)
            id += 1
        f.seek(TEXT_BLOCK2_START)
        while f.tell() < TEXT_BLOCK2_END:
            text_address = f.tell()
            text = read_text(f)
            text_encoded = table.encode(text, mte_resolver=True, dict_resolver=False, cmd_list=[(0xf6, 1), (0xfb, 5), (0xfc, 5), (0xfd, 2), (0xfe, 2), (0xff, 3)])
            # dump - db
            text_binary = sqlite3.Binary(text)
            text_length = len(text_binary)
            cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, 1)', (id, buffer(text_binary), text_encoded, text_address, '', text_length))
            # dump - txt
            filename = os.path.join(dump_path, '%s - %d.txt' % (str(id).zfill(3), text_address))
            with open(filename, 'w') as out:
                out.write(text_encoded)
            id += 1
    cur.close()
    conn.commit()
    conn.close()

def brainlord_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    translation_path = args.translation_path
    db = args.database_file
    user_name = args.user
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    # find pointers
    NEW_TEXT_BLOCK1_START = NEW_TEXT_BLOCK1_END = 0x190000
    new_pointers = OrderedDict()
    with open(dest_file, 'r+b') as fw:
        fw.seek(NEW_TEXT_BLOCK1_START)
        # db
        cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, 1))
        for row in cur:
            address = row[5]
            new_pointers[int(address)] = fw.tell()
            original_text = row[2]
            new_text = row[4]
            text = new_text if new_text else original_text
            decoded_text = table.decode(text, mte_resolver=True, dict_resolver=False)
            fw.write(decoded_text)
            fw.write(int2byte(0xf7))
        # txt
        """
        filenames = os.listdir(translation_path)
        for filename in filenames:
            id, address = filename.replace('.txt', '').split(' - ')
            new_pointers[int(address)] = fw.tell()
            with open(os.path.join(translation_path, filename), 'rb') as fr:
                text = fr.read()
                text = decode_text(text)
                decoded_text = table.decode(text, mte_resolver=True, dict_resolver=False)
                fw.write(decoded_text)
                fw.write(int2byte(0xf7))
        """
        NEW_TEXT_BLOCK1_END = fw.tell()

    # pointer block 1
    with open(dest_file, 'r+b') as fw:
        fw.seek(POINTER_BLOCK1_START)
        while (fw.tell() < POINTER_BLOCK1_END):
            repoint_text(fw, fw.tell(), new_pointers)
    # text block pointers
    with open(dest_file, 'r+b') as fw:
        fw.seek(NEW_TEXT_BLOCK1_START)
        while (fw.tell() < NEW_TEXT_BLOCK1_END):
            byte = fw.read(1)
            if byte == '\xfc':
                fw.read(2)
                repoint_text(fw, fw.tell(), new_pointers)
            elif byte == '\xff':
                repoint_text(fw, fw.tell(), new_pointers)
    # item block pointers
    with open(dest_file, 'r+b') as fw:
        pointers = item_pointers_finder(fw, ITEM_POINTERS_START, ITEM_POINTERS_END)
        for pointer in pointers:
            repoint_text(fw, pointer, new_pointers)
    # sparse pointers
    with open(dest_file, 'r+b') as fw:
        repoint_text(fw, 0x54a13, new_pointers)
        repoint_text(fw, 0x54ba9, new_pointers)
        repoint_text(fw, 0x54bb0, new_pointers)
        repoint_text(fw, 0x54bd3, new_pointers)

    cur.close()
    conn.commit()
    conn.close()

def repoint_text(fw, offset, new_pointers):
    fw.seek(offset)
    pointer = fw.read(3)
    unpacked = struct.unpack('i', pointer + '\x00')[0] - 0xc00000
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
            print('Offset: ' + int2hex(offset) + ' Value: ' + int2hex(unpacked))

def item_pointers_finder(fw, start, end):
    pointers = []
    fw.seek(start)
    while (fw.tell() < end):
        byte = fw.read(1)
        if byte == '\xc8':
            fw.seek(-3, os.SEEK_CUR)
            pointers.append(fw.tell())
            fw.seek(3, os.SEEK_CUR)
    return pointers

def brainlord_expander(args):
    source_file = args.source_file
    dest_file = args.dest_file
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    """
    dest_filename = os.path.basename(dest_file)
    dest_path = os.path.dirname(source_file)
    if os.path.exists(os.path.join(dest_path, dest_filename)):
        os.remove(os.path.join(dest_path, dest_filename))
    """
    shutil.copy(source_file, dest_file)
    with open(dest_file, 'r+b') as fw:
        fw.seek(0, 2)
        fw.write('\0' * 524288)

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.set_defaults(func=brainlord_misc_dumper)
b_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
b_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
b_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
b_parser.set_defaults(func=brainlord_misc_inserter)
c_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
c_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
c_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
c_parser.set_defaults(func=brainlord_gfx_dumper)
d_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
d_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
d_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
d_parser.set_defaults(func=brainlord_gfx_inserter)
e_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
e_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
e_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
e_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
e_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
e_parser.set_defaults(func=brainlord_text_dumper)
f_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
f_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
f_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
f_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
f_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
f_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
f_parser.add_argument('-u', '--user', action='store', dest='user', help='')
f_parser.set_defaults(func=brainlord_text_inserter)
z_parser = subparsers.add_parser('expand', help='Execute EXPANDER')
z_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
z_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
z_parser.set_defaults(func=brainlord_expander)
args = parser.parse_args()
args.func(args)
