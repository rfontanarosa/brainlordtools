__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3, shutil, csv
from collections import OrderedDict

from rhtools.utils import crc32
from rhtools3.db import insert_text, convert_to_binary, select_translation_by_author, select_most_recent_translation
from rhtools.dump import read_text, write_text, dump_binary, insert_binary
from rhtools3.Table import Table

CRC32 = 'AC443D87'

TEXT_BLOCK1_START = 0x170000
TEXT_BLOCK1_END = 0x17fac9
# TEXT_BLOCK1_LIMIT = 0x17ffff

# items descriptions
TEXT_BLOCK2_START = 0x8dec1
TEXT_BLOCK2_END = 0x8f9ed
# TEXT_BLOCK2_LIMIT = 0x903ff

TEXT_BLOCK3_START = 0x66e85
TEXT_BLOCK3_END = 0x67100

TEXT_BLOCK4_START = 0x120000
TEXT_BLOCK4_END = 0x1202f7

# 2 dialogues
TEXT_BLOCK5_START = 0x6776e
TEXT_BLOCK5_END = 0x6789f

TEXT_BLOCK6_START = 0x6660f
TEXT_BLOCK6_END = 0x669c5

TEXT_BLOCK7_START = 0x669f7
TEXT_BLOCK7_END = 0x66e77

CREDITS_BLOCK_START = 0x100000
CREDITS_BLOCK_END = 0x10084f

POINTER_BLOCK1_START = 0x50013
POINTER_BLOCK1_END = 0x50285

ITEM_POINTERS_START = 0x18a02
ITEM_POINTERS_END = 0x19388

FONT1_BLOCK = (0x74000, 0x78000)
FONT2_BLOCK = (0x80000, 0x82000)

def dump_blocks(f, table, dump_path):
    filename = os.path.join(dump_path, 'misc1.csv')
    with open(filename, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(0x67103)
        while f.tell() <= 0x6776d:
            text_address = f.tell()
            text = read_text(f, text_address, end_byte=b'\xf7')
            text_decoded = table.decode(text, mte_resolver=True, dict_resolver=False)
            fields = [hex(text_address), text_decoded]
            csv_writer.writerow(fields)
    filename = os.path.join(dump_path, 'misc2.csv')
    with open(filename, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(0x12030d)
        while f.tell() < 0x120824:
            text_address = f.tell()
            text = read_text(f, text_address, end_byte=b'\xf7')
            text_decoded = table.decode(text, mte_resolver=True, dict_resolver=False)
            fields = [hex(text_address), text_decoded]
            csv_writer.writerow(fields)
    filename = os.path.join(dump_path, 'misc3.csv')
    with open(filename, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(0x120825)
        while f.tell() < 0x1208ac:
            text_address = f.tell()
            text = read_text(f, text_address, end_byte=b'\xf7')
            text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
            fields = [hex(text_address), text_decoded]
            csv_writer.writerow(fields)

def get_pointers(f, start, count, step):
    pointers = OrderedDict()
    end = start + (count * step)
    f.seek(start)
    while f.tell() < end:
        p_offset = f.tell()
        pointer = f.read(step)
        p_value = struct.unpack('i', pointer[:3] + b'\x00')[0] - 0xc00000
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_pointer_value(f, start, step, third_byte_index=2):
    f.seek(start)
    pointer = f.read(step)
    p_value = struct.unpack('i', pointer[:2] + bytes([pointer[third_byte_index]]) + b'\x00')[0] - 0xc00000
    return p_value

def get_translated_texts(filename):
    translated_texts = OrderedDict()
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            text_address = int(row['text_address'], 16)
            translated_texts[text_address] = trans
    return translated_texts

def repoint_misc(f, pointers, new_pointers):
    for i, (p_value, p_addresses) in enumerate(pointers.items()):
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print('repoint_misc - Text not found - Text offset: ' + hex(p_value))
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                packed = struct.pack('i', p_new_value + 0xc00000)
                f.write(packed[:-1])

def repoint_misc1(f, pointers, new_pointers):
    for i, (p_value, p_addresses) in enumerate(pointers.items()):
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print('repoint_misc1 - Text not found - Text offset: ' + hex(p_value))
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                packed = struct.pack('i', p_new_value + 0xc00000)
                f.write(packed[:-2])
                f.seek(5, os.SEEK_CUR)
                f.write(packed[2:3])

def brainlord_misc_dumper(args):
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

def brainlord_credits_dumper(args):
    source_file = args.source_file
    table3_file = args.table3
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table3_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        filename = os.path.join(dump_path, 'credits.txt')
        with open(filename, 'w+') as txt_file:
            text = read_text(f, CREDITS_BLOCK_START, length=CREDITS_BLOCK_END - CREDITS_BLOCK_START)
            text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
            txt_file.write(text_decoded)

def brainlord_credits_inserter(args):
    dest_file = args.dest_file
    table3_file = args.table3
    translation_path = args.translation_path
    table = Table(table3_file)
    translation_file = os.path.join(translation_path, 'credits.txt')
    with open(translation_file, 'r') as f:
        text = f.read()
        text_encoded = table.encode(text, mte_resolver=False, dict_resolver=False)
        if len(text_encoded) != CREDITS_BLOCK_END - CREDITS_BLOCK_START:
            raise Exception("Invalid credits file lenght! {} - {}".format(len(text_encoded), CREDITS_BLOCK_END - CREDITS_BLOCK_START))
        with open(dest_file, 'r+b') as f1:
            f1.seek(CREDITS_BLOCK_START)
            f1.write(text_encoded)

def brainlord_misc_inserter(args):
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
        p_1_1 = get_pointers(f, 0x18a0f, 40, 13)
        p_1_2 = get_pointers(f, 0x18c17, 64, 10)
        p_1_3 = get_pointers(f, 0x18e97, 41, 13)
        p_1_4 = get_pointers(f, 0x1909f, 81, 10) # Copper Sword...
        p_1_5 = get_pointers(f, 0x193c9, 30, 12)
        # get misc2 pointers
        p_2_1 = get_pointers(f, 0x16f54, 16, 18) # Remeer... Jima
        p_2_2 = get_pointers(f, 0x17210, 16, 7) # Ason...
        p_2_3 = get_pointers(f, 0x65b7e, 65, 6) # Arcs...
        p_2_4 = get_pointers(f, 0x60658, 12, 3) # Morguai...
        p_2_5 = get_pointers(f, 0x164b, 5, 3) # Items, Magic, Config., Status, Return
        p_2_6 = get_pointers(f, 0x1980, 2, 3) # Message, Key
        p_2_7 = get_pointers(f, 0x1b57, 3, 3) # Attack......, Jump........, Defense.....
        p_2_8 = get_pointers(f, 0x2232d, 4, 3) # Buy, Trade, Sell, Quit
        p_2_9 = get_pointers(f, 0x2353b, 3, 3) # Buy, Sell, Quit
        p_2_10 = get_pointers(f, 0x23edb, 2, 3) # Buy, Quit
        p_2_11 = get_pointers(f, 0x24491, 3, 3) # Buy, Sell, Quit
        p_2_12 = get_pointers(f, 0x140860, 2, 3) # Continue, Erase
        p_2_13 = get_pointers(f, 0x14086a, 1, 3) # Beginning
        p_2_14 = get_pointers(f, 0x140871, 4, 3) # Continue, Beginning, Erase, Copy
        p_2_15 = get_pointers(f, 0x1ead, 3, 3) # Fast, Normal, Slow
        p_2_16 = get_pointers(f, 0x1b63, 2, 3) # Enter Com. , Cancel Com. 
        p_2_17 = get_pointers(f, 0x140a51, 2, 3) # Erase, Quit
        p_2_18 = get_pointers(f, 0x140ca6, 2, 3) # Copy, Quit
        p_2_19 = get_pointers(f, 0x2950, 3, 3) # Equ., Copy, Dis.
        p_2_20 = get_pointers(f, 0x295d, 3, 3) # Use, Copy, Dis.
        p_2_21 = get_pointers(f, 0x22f6, 4, 3) # LV, Power, Ex,  ^
        p_2_22 = get_pointers(f, 0x1ddbc, 11, 3) # Warp, Escape, Flag, Items, Level, Slow, Time, Set, Task, Sound, Memory
        p_2_23 = get_pointers(f, 0x2c92f, 2, 3) # Yes, No
        p_2_24 = get_pointers(f, 0x2516b, 1, 3) # The end
        p_2_25 = get_pointers(f, 0x2563e, 1, 3) # Quit
        # get misc2 other pointers
        p_b_offsets = []
        p_b_offsets.append(0x16b5) # Magic
        p_b_offsets.append(0x2316) # Items
        p_b_offsets.append(0x240e) # Items
        p_b_offsets.append(0x2a36) # Items
        p_b_offsets.append(0x21ff2) # Items
        p_b_offsets.append(0x2b74d) # Poison
        p_b_offsets.append(0x2b782) # Paralysis
        p_b_offsets.append(0x2b7ad) # HP
        p_b_offsets.append(0x2b7d8) # Power
        p_b_offsets.append(0x2b803) # Guard
        p_b_offsets.append(0x141219) # Free
        p_b_offsets.append(0x1412d3) # Free
        p_b_1 = OrderedDict()
        for p_offset in p_b_offsets:
            p_value = get_pointer_value(f, p_offset, 8, 7)
            p_b_1.setdefault(p_value, []).append(p_offset)
        # get misc3 pointers
        p_3_1 = get_pointers(f, 0x6051f, 38, 3) # MTE
    # repoint text
    with open(dest_file, 'r+b') as f1:
        # reading misc1.csv and writing texts
        translation_file = os.path.join(translation_path, 'misc1.csv')
        translated_texts = get_translated_texts(translation_file)
        new_pointers = OrderedDict()
        t_new_address = 0x180000
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            new_pointers[t_address] = t_new_address
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            t_new_address = write_text(f1, t_new_address, text, end_byte=b'\xf7')
        # repointing misc1
        for curr_pointers in (p_1_1, p_1_2, p_1_3, p_1_4, p_1_5):
            repoint_misc(f1, curr_pointers, new_pointers)
        # reading misc2.csv and writing texts
        translation_file = os.path.join(translation_path, 'misc2.csv')
        translated_texts = get_translated_texts(translation_file)
        new_pointers = OrderedDict()
        t_new_address = 0x182000
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            new_pointers[t_address] = t_new_address
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            t_new_address = write_text(f1, t_new_address, text, end_byte=b'\xf7')
        # repointing misc2
        for curr_pointers in (p_2_1, p_2_2, p_2_3, p_2_4, p_2_5, p_2_6, p_2_7, p_2_8, p_2_9, p_2_10, p_2_11, p_2_12, p_2_13, p_2_14, p_2_15, p_2_16, p_2_17, p_2_18, p_2_19, p_2_20, p_2_21, p_2_22, p_2_23, p_2_24, p_2_25):
            repoint_misc(f1, curr_pointers, new_pointers)
        # repointing other misc2
        repoint_misc1(f1, p_b_1, new_pointers)
        # reading misc3.csv and writing texts
        translation_file = os.path.join(translation_path, 'misc3.csv')
        translated_texts = get_translated_texts(translation_file)
        new_pointers = OrderedDict()
        t_new_address = 0x184000
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            new_pointers[t_address] = t_new_address
            text = table2.encode(t_value, mte_resolver=False, dict_resolver=False)
            t_new_address = write_text(f1, t_new_address, text, end_byte=b'\xf7')
        # repointing misc3
        repoint_misc(f1, p_3_1, new_pointers)

def brainlord_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[1], dump_path, 'gfx_font1.bin')
        dump_binary(f, FONT2_BLOCK[0], FONT2_BLOCK[1], dump_path, 'gfx_font2.bin')

def brainlord_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[1], translation_path, 'gfx_font1.bin')
        insert_binary(f, FONT2_BLOCK[0], FONT2_BLOCK[1], translation_path, 'gfx_font2.bin')

def brainlord_bank_dumper(f, dump_path, table, id, block, cur, start=0x0, end=0x0):
    f.seek(start)
    while f.tell() < end:
        text_address = f.tell()
        text = read_text(f, text_address, end_byte=b'\xf7', cmd_list={b'\xfc': 5})
        text_decoded = table.decode(text, mte_resolver=True, dict_resolver=False, cmd_list={0xf6: 1, 0xfb: 5, 0xfc: 5, 0xfd: 2, 0xfe: 2, 0xff: 3})
        # dump - db
        insert_text(cur, id, convert_to_binary(text), text_decoded, text_address, '', block, '')
        # dump - txt
        filename = os.path.join(dump_path, 'dump_eng.txt')
        with open(filename, 'a+') as out:
            out.write(text_decoded)
        id += 1
    return id

def brainlord_text_dumper(args):
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
        id = brainlord_bank_dumper(f, dump_path, table, id, 1, cur, TEXT_BLOCK1_START, TEXT_BLOCK1_END)
        id = brainlord_bank_dumper(f, dump_path, table, id, 2, cur, TEXT_BLOCK2_START, TEXT_BLOCK2_END)
        id = brainlord_bank_dumper(f, dump_path, table, id, 3, cur, TEXT_BLOCK3_START, TEXT_BLOCK3_END)
        id = brainlord_bank_dumper(f, dump_path, table, id, 4, cur, TEXT_BLOCK4_START, TEXT_BLOCK4_END)
        id = brainlord_bank_dumper(f, dump_path, table, id, 5, cur, TEXT_BLOCK5_START, TEXT_BLOCK5_END)
        id = brainlord_bank_dumper(f, dump_path, table, id, 6, cur, TEXT_BLOCK6_START, TEXT_BLOCK6_END)
        id = brainlord_bank_dumper(f, dump_path, table, id, 7, cur, TEXT_BLOCK7_START, TEXT_BLOCK7_END)
    cur.close()
    conn.commit()
    conn.close()

def brainlord_text_inserter(args):
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
    # find pointers
    NEW_TEXT_BLOCK1_START = NEW_TEXT_BLOCK1_END = 0x190000
    new_pointers = OrderedDict()
    with open(dest_file, 'r+b') as fw:
        fw.seek(NEW_TEXT_BLOCK1_START)
        # db
        rows = select_most_recent_translation(cur, ['1', '2', '3', '4', '5', '6', '7'])
        for row in rows:
            address = row[3]
            text_decoded = row[2]
            translation = row[5]
            text = translation if translation else text_decoded
            encoded_text = table.encode(text, mte_resolver=True, dict_resolver=False)
            if fw.tell() < 0x1a0000 and fw.tell() + len(encoded_text) > 0x19ffff:
                fw.seek(0x1a0000)
            new_pointers[int(address)] = fw.tell()
            fw.write(encoded_text)
            fw.write(b'\xf7')
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
            if byte in (b'\xfb', b'\xfc'):
                fw.read(2)
                repoint_text(fw, fw.tell(), new_pointers)
            elif byte == b'\xff':
                repoint_text(fw, fw.tell(), new_pointers)
    # item block pointers
    with open(dest_file, 'r+b') as fw:
        pointers = item_pointers_finder(fw, ITEM_POINTERS_START, ITEM_POINTERS_END)
        for pointer in pointers:
            repoint_text(fw, pointer, new_pointers)
    # sparse pointers
    with open(dest_file, 'r+b') as fw:
        #
        repoint_text(fw, 0x434c2, new_pointers)
        #
        repoint_text(fw, 0x5145f, new_pointers)
        repoint_text(fw, 0x518e2, new_pointers)
        repoint_text(fw, 0x519c9, new_pointers)
        repoint_text(fw, 0x51a94, new_pointers)
        repoint_text(fw, 0x51ada, new_pointers)
        repoint_text(fw, 0x51ae1, new_pointers)
        repoint_text(fw, 0x51ae8, new_pointers)
        #
        fw.seek(0x51c31)
        while (fw.tell() < 0x51c64):
            repoint_text(fw, fw.tell(), new_pointers)
            fw.seek(4, os.SEEK_CUR)
        #
        fw.seek(0x18ea1)
        while (fw.tell() < 0x18f9a):
            repoint_text(fw, fw.tell(), new_pointers)
            fw.seek(10, os.SEEK_CUR)
        #
        fw.seek(0x19390)
        while (fw.tell() < 0x193ce):
            repoint_text(fw, fw.tell(), new_pointers)
            fw.seek(7, os.SEEK_CUR)
        fw.seek(0x193d8)
        while (fw.tell() < 0x19536):
            repoint_text(fw, fw.tell(), new_pointers)
            fw.seek(9, os.SEEK_CUR)
        #
        repoint_text(fw, 0x51de3, new_pointers)
        repoint_text(fw, 0x51dea, new_pointers)
        repoint_text(fw, 0x51df1, new_pointers)
        repoint_text(fw, 0x51df8, new_pointers)
        repoint_text(fw, 0x51e5a, new_pointers)
        repoint_text(fw, 0x51e61, new_pointers)
        repoint_text(fw, 0x51e68, new_pointers)
        repoint_text(fw, 0x51e6f, new_pointers)
        repoint_text(fw, 0x51e76, new_pointers)
        #
        repoint_text(fw, 0x51f09, new_pointers)
        repoint_text(fw, 0x51ff0, new_pointers)
        #
        repoint_text(fw, 0x52592, new_pointers)
        repoint_text(fw, 0x52767, new_pointers)
        repoint_text(fw, 0x5276e, new_pointers)
        repoint_text(fw, 0x52775, new_pointers)
        repoint_text(fw, 0x5277c, new_pointers)
        #
        repoint_text(fw, 0x528a9, new_pointers)
        repoint_text(fw, 0x528b0, new_pointers)
        #
        repoint_text(fw, 0x52989, new_pointers)
        repoint_text(fw, 0x52990, new_pointers)
        repoint_text(fw, 0x52997, new_pointers)
        repoint_text(fw, 0x5299e, new_pointers)
        repoint_text(fw, 0x529a5, new_pointers)
        repoint_text(fw, 0x52aa8, new_pointers)
        repoint_text(fw, 0x52aaf, new_pointers)
        repoint_text(fw, 0x52ab6, new_pointers)
        repoint_text(fw, 0x52abd, new_pointers)
        repoint_text(fw, 0x52ac4, new_pointers)
        repoint_text(fw, 0x52acb, new_pointers)
        repoint_text(fw, 0x52ad2, new_pointers)
        #
        repoint_text(fw, 0x52bb9, new_pointers)
        #
        repoint_text(fw, 0x52f24, new_pointers)
        repoint_text(fw, 0x52f55, new_pointers)
        repoint_text(fw, 0x52ff6, new_pointers)
        repoint_text(fw, 0x53012, new_pointers)
        repoint_text(fw, 0x531af, new_pointers)
        repoint_text(fw, 0x53306, new_pointers)
        repoint_text(fw, 0x533df, new_pointers)
        repoint_text(fw, 0x5329d, new_pointers)
        repoint_text(fw, 0x534a3, new_pointers)
        repoint_text(fw, 0x534b8, new_pointers)
        repoint_text(fw, 0x534f7, new_pointers)
        repoint_text(fw, 0x5350c, new_pointers)
        #
        repoint_text(fw, 0x53624, new_pointers)
        repoint_text(fw, 0x5362b, new_pointers)
        repoint_text(fw, 0x53632, new_pointers)
        repoint_text(fw, 0x53639, new_pointers)
        repoint_text(fw, 0x53640, new_pointers)
        repoint_text(fw, 0x53647, new_pointers)
        repoint_text(fw, 0x5364e, new_pointers)
        repoint_text(fw, 0x53655, new_pointers)
        repoint_text(fw, 0x5365c, new_pointers)
        repoint_text(fw, 0x53663, new_pointers)
        #
        repoint_text(fw, 0x537c8, new_pointers)
        repoint_text(fw, 0x537cf, new_pointers)
        repoint_text(fw, 0x537d6, new_pointers)
        repoint_text(fw, 0x537dd, new_pointers)
        repoint_text(fw, 0x537e4, new_pointers)
        repoint_text(fw, 0x537eb, new_pointers)
        repoint_text(fw, 0x537f2, new_pointers)
        repoint_text(fw, 0x53934, new_pointers)
        repoint_text(fw, 0x5393b, new_pointers)
        repoint_text(fw, 0x53942, new_pointers)
        repoint_text(fw, 0x53949, new_pointers)
        repoint_text(fw, 0x53950, new_pointers)
        repoint_text(fw, 0x53957, new_pointers)
        repoint_text(fw, 0x5395e, new_pointers)
        repoint_text(fw, 0x53965, new_pointers)
        repoint_text(fw, 0x5396c, new_pointers)
        repoint_text(fw, 0x53973, new_pointers)
        repoint_text(fw, 0x5397a, new_pointers)
        repoint_text(fw, 0x53981, new_pointers)
        repoint_text(fw, 0x53a53, new_pointers)
        #
        repoint_text(fw, 0x53cc2, new_pointers)
        repoint_text(fw, 0x53e04, new_pointers)
        repoint_text(fw, 0x53e0b, new_pointers)
        repoint_text(fw, 0x53ecf, new_pointers)
        repoint_text(fw, 0x53ed6, new_pointers)
        #
        repoint_text(fw, 0x54264, new_pointers)
        repoint_text(fw, 0x54279, new_pointers)
        repoint_text(fw, 0x54391, new_pointers)
        repoint_text(fw, 0x54398, new_pointers)
        repoint_text(fw, 0x5439f, new_pointers)
        repoint_text(fw, 0x543a6, new_pointers)
        repoint_text(fw, 0x54471, new_pointers)
        repoint_text(fw, 0x5461c, new_pointers)
        repoint_text(fw, 0x54623, new_pointers)
        repoint_text(fw, 0x5462a, new_pointers)
        repoint_text(fw, 0x54693, new_pointers)
        repoint_text(fw, 0x54757, new_pointers)
        repoint_text(fw, 0x5475e, new_pointers)
        repoint_text(fw, 0x547ce, new_pointers)
        repoint_text(fw, 0x547d5, new_pointers)
        repoint_text(fw, 0x54a13, new_pointers)
        repoint_text(fw, 0x54a36, new_pointers)
        repoint_text(fw, 0x54a3d, new_pointers)
        repoint_text(fw, 0x54a91, new_pointers)
        repoint_text(fw, 0x54ab4, new_pointers)
        repoint_text(fw, 0x54af3, new_pointers)
        #
        repoint_text(fw, 0x54b47, new_pointers)
        repoint_text(fw, 0x54b71, new_pointers)
        repoint_text(fw, 0x54b9b, new_pointers)
        repoint_text(fw, 0x54ba9, new_pointers)
        repoint_text(fw, 0x54bb0, new_pointers)
        repoint_text(fw, 0x54bc5, new_pointers)
        repoint_text(fw, 0x54bd3, new_pointers)
        repoint_text(fw, 0x54c27, new_pointers)
        repoint_text(fw, 0x54d4d, new_pointers)
        repoint_text(fw, 0x54d70, new_pointers)
        repoint_text(fw, 0x54da8, new_pointers)
        repoint_text(fw, 0x54dc4, new_pointers)
        repoint_text(fw, 0x54de7, new_pointers)
        repoint_text(fw, 0x54e5e, new_pointers)
        repoint_text(fw, 0x54e81, new_pointers)
        repoint_text(fw, 0x54e8f, new_pointers)
        repoint_text(fw, 0x54eab, new_pointers)
        repoint_text(fw, 0x54eb2, new_pointers)
        repoint_text(fw, 0x54edc, new_pointers)
        repoint_text(fw, 0x54f3e, new_pointers)
        repoint_text(fw, 0x54f53, new_pointers)
        repoint_text(fw, 0x54fe6, new_pointers)
        repoint_text(fw, 0x550b8, new_pointers)
        repoint_text(fw, 0x550bf, new_pointers)
        #
        repoint_text(fw, 0x55278, new_pointers)
        repoint_text(fw, 0x5527f, new_pointers)
        repoint_text(fw, 0x55286, new_pointers)
        repoint_text(fw, 0x5528d, new_pointers)
        repoint_text(fw, 0x55294, new_pointers)
        repoint_text(fw, 0x5529b, new_pointers)
        repoint_text(fw, 0x552a2, new_pointers)
        repoint_text(fw, 0x552a9, new_pointers)
        repoint_text(fw, 0x552b0, new_pointers)
        repoint_text(fw, 0x552b7, new_pointers)
        repoint_text(fw, 0x552be, new_pointers)
        repoint_text(fw, 0x552c5, new_pointers)
        repoint_text(fw, 0x552cc, new_pointers)
        repoint_text(fw, 0x552d3, new_pointers)
        repoint_text(fw, 0x552da, new_pointers)
        repoint_text(fw, 0x552e1, new_pointers)
        repoint_text(fw, 0x552e8, new_pointers)
        repoint_text(fw, 0x552ef, new_pointers)
        repoint_text(fw, 0x552f6, new_pointers)
        #
        repoint_text(fw, 0x553c1, new_pointers)
        repoint_text(fw, 0x553c8, new_pointers)
        repoint_text(fw, 0x553cf, new_pointers)
        repoint_text(fw, 0x553d6, new_pointers)
        repoint_text(fw, 0x553dd, new_pointers)
        repoint_text(fw, 0x553e4, new_pointers)
        repoint_text(fw, 0x553eb, new_pointers)
        repoint_text(fw, 0x553f2, new_pointers)
        repoint_text(fw, 0x553f9, new_pointers)
        repoint_text(fw, 0x55400, new_pointers)
        repoint_text(fw, 0x55407, new_pointers)
        repoint_text(fw, 0x5540e, new_pointers)
        repoint_text(fw, 0x55415, new_pointers)
        repoint_text(fw, 0x5541c, new_pointers)
        repoint_text(fw, 0x55423, new_pointers)
        repoint_text(fw, 0x5542a, new_pointers)
        repoint_text(fw, 0x55431, new_pointers)
        repoint_text(fw, 0x55438, new_pointers)
        repoint_text(fw, 0x5543f, new_pointers)
        repoint_text(fw, 0x55446, new_pointers)
        repoint_text(fw, 0x5544d, new_pointers)
        repoint_text(fw, 0x5549a, new_pointers)
        repoint_text(fw, 0x554a1, new_pointers)
        repoint_text(fw, 0x554a8, new_pointers)
        repoint_text(fw, 0x554e7, new_pointers)
        repoint_text(fw, 0x554ee, new_pointers)
        repoint_text(fw, 0x5551f, new_pointers)
        repoint_text(fw, 0x55526, new_pointers)
        repoint_text(fw, 0x55534, new_pointers)
        repoint_text(fw, 0x55565, new_pointers)
        repoint_text(fw, 0x668ed, new_pointers)
        repoint_text(fw, 0x669f1, new_pointers)
    #
    with open(dest_file, 'r+b') as fw:
        fw.seek(0xf86)
        while (fw.tell() < 0xfee):
            repoint_text(fw, fw.tell(), new_pointers)
    # two bytes pointers
    with open(dest_file, 'r+b') as fw:
        repoint_two_bytes_pointers(fw, 0x2990, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0x2cc0, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0x2cf3, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0xa137, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0xa14e, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0x221e8, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x2234c, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x223c3, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x2254c, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x225ff, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22616, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22627, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22786, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x227c0, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x227d9, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22803, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x229a7, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22a5f, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22cec, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23099, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x2313e, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23155, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23166, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x231d6, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x2332c, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x2334d, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23406, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x234ec, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23a2c, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23c59, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23c7a, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23da6, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23e8c, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23f7c, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23fb9, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x240e1, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x2435c, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x2422c, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x244da, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x24518, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x247d3, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x247f0, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x24bf6, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x24c17, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x24c55, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0x24d3a, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0x248fc, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x21cb9, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x21daf, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x21e05, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x21e57, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x21eb6, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x21ed7, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x222de, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22949, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22ca9, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x22f23, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x232ef, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x237e6, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23946, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x235ce, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x23b32, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x24442, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x24730, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x251c2, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x251e8, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x25253, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x252a4, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x25664, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x25a6e, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x25bcd, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x25c07, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x26623, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x6f06e, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x14005d, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0x140140, new_pointers, b'\xc6')
        repoint_two_bytes_pointers(fw, 0x143902, new_pointers, b'\xd7')
        repoint_two_bytes_pointers(fw, 0x1496f2, new_pointers, b'\xd7')

    cur.close()
    conn.commit()
    conn.close()

def repoint_two_bytes_pointers(fw, offset, new_pointers, third_byte):
    fw.seek(offset)
    pointer = fw.read(2)
    unpacked = struct.unpack('i', pointer + third_byte + b'\x00')[0] - 0xc00000
    new_pointer = new_pointers.get(unpacked)
    if new_pointer:
        fw.seek(-2, os.SEEK_CUR)
        packed = struct.pack('i', new_pointer + 0xc00000)
        fw.write(packed[:-2])
        fw.seek(6, os.SEEK_CUR)
        fw.write(packed[2:3])
    else:
        print('CHOICE - Pointer offset: ' + hex(offset) + ' Text offset: ' + hex(unpacked))

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
            print('TEXT - Pointer offset: ' + hex(offset) + ' Text offset: ' + hex(unpacked))

def item_pointers_finder(fw, start, end):
    pointers = []
    fw.seek(start)
    while (fw.tell() < end):
        byte = fw.read(1)
        if byte in (b'\xc6', b'\xc8'):
            fw.seek(-3, os.SEEK_CUR)
            pointers.append(fw.tell())
            fw.seek(3, os.SEEK_CUR)
    return pointers

def brainlord_expander(args):
    source_file = args.source_file
    dest_file = args.dest_file
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.copy(source_file, dest_file)
    with open(dest_file, 'r+b') as f:
        f.seek(0, os.SEEK_END)
        f.write(b'\x00' * 524288)

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
dump_text_parser.set_defaults(func=brainlord_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=brainlord_text_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=brainlord_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=brainlord_gfx_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=brainlord_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=brainlord_misc_inserter)
expand_parser = subparsers.add_parser('expand', help='Execute EXPANDER')
expand_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
expand_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
expand_parser.set_defaults(func=brainlord_expander)
dump_credits_parser = subparsers.add_parser('dump_credits', help='Execute CREDITS DUMP')
dump_credits_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_credits_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Credits table filename')
dump_credits_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_credits_parser.set_defaults(func=brainlord_credits_dumper)
insert_credits_parser = subparsers.add_parser('insert_credits', help='Execute CREDITS INSERTER')
insert_credits_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_credits_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Credits table filename')
insert_credits_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_credits_parser.set_defaults(func=brainlord_credits_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
