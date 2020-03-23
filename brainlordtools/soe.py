# -*- coding: utf-8 -*-

__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, shutil, csv
from collections import OrderedDict

from rhtools.utils import crc32, byte2int, int2byte, int2hex, string_address2int_address
from rhtools.Table import Table

CRC32 = 'A5C0045E'

TEXT_BLOCK = OrderedDict()
TEXT_BLOCK['currency_names'] = (0x460AE, 0x460CF)
TEXT_BLOCK['weapons_names'] = (0x460D0, 0x46195)
TEXT_BLOCK['weapons_descriptions'] = (0x46196, 0x463CC)
TEXT_BLOCK['armor_names'] = (0x463CD, 0x465DC)
TEXT_BLOCK['debug'] = (0x465DD, 0x467E8)
TEXT_BLOCK['alchemy_names'] = (0x467E9, 0x4692B)
TEXT_BLOCK['alchemy_descriptions'] = (0x4692C, 0x46C77)
TEXT_BLOCK['alchemy_ingredient_names'] = (0x46C78, 0x46D1B)
TEXT_BLOCK['call_bead_summon_names'] = (0x46D1C, 0x46D3C)
TEXT_BLOCK['call_bead_spell_names'] = (0x46D3D, 0x46DD2)
TEXT_BLOCK['npc_enemy_names1'] = (0x46DD3, 0x471FA)
TEXT_BLOCK['item_names'] = (0x471FB, 0x47249)
TEXT_BLOCK['npc_enemy_names2'] = (0x4724A, 0x47256)
TEXT_BLOCK['trade_good_names'] = (0x47257, 0x472E9)
TEXT_BLOCK['charm_names'] = (0x472EA, 0x47396)
TEXT_BLOCK['rare_item_names'] = (0x47397, 0x473D3)
TEXT_BLOCK['rare_item_descriptions'] = (0x473D4, 0x473DD)
TEXT_BLOCK['charm_descriptions'] = (0x473DE, 0x47712)

FONT1_BLOCK = (0x40002, 0x40C01) #24bit - 3byte
FONT1_VWF_TABLE = (0x40C02, 0x40C81) #127
FONT2_BLOCK = (0x40C84, 0x41883) #24bit - 3byte
FONT2_VWF_TABLE = (0x41884, 0x41903) #127

def read_text(f, end_byte=0x00):
    text = b''
    byte = b'1'
    while not byte2int(byte) == end_byte:
        byte = f.read(1)
        if byte2int(byte) != end_byte:
            text += byte
    return text

def decode_text(text):
    text = text.replace(u'à', '{11}')
    text = text.replace(u'è', '{13}')
    text = text.replace(u'é', '{15}')
    text = text.replace(u'ì', '{17}')
    text = text.replace(u'ò', '{19}')
    text = text.replace(u'ù', '{1B}')
    text = text.replace(u'È', '{1D}')
    return text

def write_text(f, offset, text, table, end_byte=0x00, limit=None):
    f.seek(offset)
    text = decode_text(text)
    decoded_text = table.decode(text, mte_resolver=False, dict_resolver=False)
    f.write(decoded_text)
    f.write(int2byte(end_byte))
    if limit and f.tell() > limit:
        raise Exception()
    return f.tell()

def dump_block(f, table, dump_path):
    for block_name, block_limits in TEXT_BLOCK.iteritems():
        filename = os.path.join(dump_path, block_name + '.csv')
        with open(filename, 'wb+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(block_limits[0])
            while f.tell() < block_limits[1]:
                text_address = f.tell()
                text = read_text(f)
                text_encoded = table.encode(text)
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

def get_currency_names_pointers(f, block_limits=(0xf8704, 0xf870f)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while f.tell() < block_limits[1]:
        p_offset = f.tell()
        pointer = f.read(3)
        p_value = string_address2int_address(pointer[:2], switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_ring_pointers(f, block_limits=(0xe814c, 0xe8653)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(8)
        p_value = string_address2int_address(pointer[:2], switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_alchemy_names_pointers(f, block_limits=(0x45d09, 0x45d4e)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_alchemy_descriptions_pointers(f, block_limits=(0x45d51, 0x45d96)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_alchemy_ingredient_names_pointers(f, block_limits=(0x45fc5, 0x4601e)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_weapon_names_pointers(f):
    pointers = OrderedDict()
    for start in (0xd8c3e, 0xd8e17, 0xd8fee):
        f.seek(start)
        while(f.tell() < start + (112*4)):
            p_offset = f.tell() +3
            pointer = f.read(112)
            p_value = string_address2int_address(pointer[3:5], switch=True, offset=0x40000)
            pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_weapon_descriptions_pointers(f, block_limits=(0x459fa, 0x45a11)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_status_weapons_pointers(f, block_limits=(0x438e8, 0x43b04)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while (f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(36)
        p_value = string_address2int_address(pointer[:2], switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_status_armors_pointers(f, block_limits=(0x43b06, 0x43c96)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while (f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(10)
        p_value = string_address2int_address(pointer[:2], switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_trade_goods_pointers(f, block_limits=(0xcbc00, 0xcbc19)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_charm_names_pointers(f, block_limits=(0xcbc1a, 0xcbc35)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_charm_descriptions_pointers(f, block_limits=(0xcc3d0, 0xcc3eb)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_rare_items_pointers(f, block_limits=(0xcbc36, 0xcbc42)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_rare_item_descriptions_pointers(f, block_limits=(0xcc3ec, 0xcc3f7)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while(f.tell() < block_limits[1]):
        p_offset = f.tell()
        pointer = f.read(2)
        p_value = string_address2int_address(pointer, switch=True, offset=0x40000)
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_npc_enemy_names_pointers(f, block_limits=(0xeb70c, 0xedf84)):
    pointers = OrderedDict()
    f.seek(block_limits[0])
    while f.tell() < block_limits[1]:
        p_offset = f.tell()
        pointer = f.read(74)
        p_value = string_address2int_address(pointer[:2], switch=True, offset=0x40000)
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

def repoint_misc(filename, f, table, next_text_address=0x360000):
    with open(filename, 'rb') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            text_address = row.get('text_address')
            if text_address:
                p_addresses = row.get('pointer_addresses')
                if p_addresses:
                    for p_address in p_addresses.split(','):
                        p_address = int(p_address, 16)
                        f.seek(p_address)
                        pointer = f.read(6)
                        if text_address in ('0xd9f43', '0xd9f53'):
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            f.seek(p_address)
                            f.write(new_pointer)
                            f.seek(0xd9f24)
                            f.write(int2byte(0xf6))
                        elif text_address in ('0xda692', '0xda69b'):
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            f.seek(p_address)
                            f.write(new_pointer)
                            f.seek(0xda2bc)
                            f.write(int2byte(0xf6))
                        elif text_address in ('0xdaf68', '0xdaf71'):
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            f.seek(p_address)
                            f.write(new_pointer)
                            f.seek(0xdab67)
                            f.write(int2byte(0xf6))
                        elif text_address == '0xddef3':
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            f.seek(p_address)
                            f.write(new_pointer)
                        else:
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            new_pointer += pointer[2:5]
                            new_pointer += int2byte(0xf6)
                            f.seek(p_address)
                            f.write(new_pointer)
                    trans = row.get('trans2') or row.get('trans1') or row.get('text')
                    trans = trans.decode('utf8')
                    next_text_address = write_text(f, next_text_address, trans, table)

def repoint(f, pointers, new_pointers, offset=0x40000):
    for p_value, p_addresses in pointers.iteritems():
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print('NOT FOUND 1')
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                f.write(struct.pack('H', p_new_value - offset))

def repoint_npc_enemy_names(f, pointers, new_pointers, offset=0x340000):
    for p_value, p_addresses in pointers.iteritems():
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print('NOT FOUND 2')
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                f.write(struct.pack('H', p_new_value - offset))
                f.write(int2byte(int(0xf4)))

def soe_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_block(f, table, dump_path)

def soe_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    translation_path = args.translation_path
    misc_file1 = args.misc_file1
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    with open(source_file, 'rb') as f0:
        pointers00 = get_currency_names_pointers(f0)
        pointers0 = get_ring_pointers(f0)
        pointers1 = get_alchemy_names_pointers(f0)
        pointers2 = get_alchemy_descriptions_pointers(f0)
        pointers3 = get_alchemy_ingredient_names_pointers(f0)
        pointers4 = get_weapon_names_pointers(f0)
        pointers5 = get_weapon_descriptions_pointers(f0)
        pointers6 = get_status_weapons_pointers(f0)
        pointers7 = get_status_armors_pointers(f0)
        pointers8 = get_trade_goods_pointers(f0)
        pointers9 = get_charm_names_pointers(f0)
        pointers10 = get_charm_descriptions_pointers(f0)
        pointers11 = get_rare_items_pointers(f0)
        pointers12 = get_rare_item_descriptions_pointers(f0)
        pointers13 = get_npc_enemy_names_pointers(f0)
    with open(dest_file, 'r+b') as f1:
        translated_blocks = OrderedDict()
        for block_name, block_limits in TEXT_BLOCK.iteritems():
            translation_file = os.path.join(translation_path, block_name + '.csv')
            translated_blocks[block_name] = get_translated_texts(translation_file)
        # new pointers
        new_pointers = OrderedDict()
        t_new_address = 0x460ae
        for block_name, translated_texts in translated_blocks.iteritems():
            for t_address, t_value in translated_texts.iteritems():
                new_pointers[t_address] = t_new_address
                if block_name not in ('npc_enemy_names1', 'npc_enemy_names2'):
                    t_new_address = write_text(f1, t_new_address, t_value, table, limit=0x47712)
                else:
                    t_new_address = write_text(f1, t_new_address, 'X', table, limit=0x47712)
        # repointing
        for curr_pointers in (pointers00, pointers0, pointers1, pointers2, pointers3, pointers4, pointers5, pointers6, pointers7, pointers8, pointers9, pointers10, pointers11, pointers12):
            repoint(f1, curr_pointers, new_pointers)
        # npc/enemies new pointers
        new_pointers = OrderedDict()
        t_new_address = 0x340000
        for block_name, translated_texts in translated_blocks.iteritems():
            if block_name in ('npc_enemy_names1', 'npc_enemy_names2'):
                for t_address, t_value in translated_texts.iteritems():
                    new_pointers[t_address] = t_new_address
                    t_new_address = write_text(f1, t_new_address, t_value, table)
        # repointing npc/enemies
        repoint_npc_enemy_names(f1, pointers13, new_pointers)
        # misc
        repoint_misc(misc_file1, f1, table)

def soe_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_gfx(f, FONT1_BLOCK[0], FONT1_BLOCK[1] - (16 * 8 * 3), dump_path, 'gfx_font1.bin')
        dump_gfx(f, FONT1_VWF_TABLE[0], FONT1_VWF_TABLE[1] - 16, dump_path, 'gfx_vwf1.bin')
        dump_gfx(f, FONT2_BLOCK[0], FONT2_BLOCK[1] - (16 * 8 * 3), dump_path, 'gfx_font2.bin')
        dump_gfx(f, FONT2_VWF_TABLE[0], FONT2_VWF_TABLE[1] - 16, dump_path, 'gfx_vwf2.bin')
        dump_gfx(f, FONT1_BLOCK[0], FONT1_BLOCK[0] + (16 * 8 * 3), dump_path, 'gfx_exp_font1.bin')
        dump_gfx(f, FONT1_VWF_TABLE[0], FONT1_VWF_TABLE[0] + 16, dump_path, 'gfx_exp_vwf1.bin')
        dump_gfx(f, FONT2_BLOCK[0], FONT2_BLOCK[0] + (16 * 8 * 3), dump_path, 'gfx_exp_font2.bin')
        dump_gfx(f, FONT2_VWF_TABLE[0], FONT2_VWF_TABLE[0] + 16, dump_path, 'gfx_exp_vwf2.bin')

def soe_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        f.seek(0xC9ED8)
        f.write(int2byte(0x10))
        f.seek(0xCA54F)
        f.write(int2byte(0x10))
        f.seek(0xCA5A4)
        f.write(int2byte(0x10))
        f.seek(0xCA92A)
        f.write(int2byte(0x10))
        f.seek(0xCB9B8)
        f.write(int2byte(0x10))
        f.seek(0xCB9FD)
        f.write(int2byte(0x10))
        f.seek(0xCBB21)
        f.write(int2byte(0x10))
        f.seek(0xCC951)
        f.write(int2byte(0x10))
        #
        f.seek(0xC9E8B)
        f.write(int2byte(0xa9))
        f.write(int2byte(0x71))
        f.seek(0xCA492)
        f.write(int2byte(0xa9))
        f.write(int2byte(0x71))
        #
        insert_gfx(f, FONT1_BLOCK[0] + (16 * 8 * 3), FONT1_BLOCK[1], translation_path, 'gfx_font1.bin')
        insert_gfx(f, FONT1_VWF_TABLE[0] + 16, FONT1_VWF_TABLE[1], translation_path, 'gfx_vwf1.bin')
        insert_gfx(f, FONT2_BLOCK[0] + (16 * 8 * 3), FONT2_BLOCK[1], translation_path, 'gfx_font2.bin')
        insert_gfx(f, FONT2_VWF_TABLE[0] + 16, FONT2_VWF_TABLE[1], translation_path, 'gfx_vwf2.bin')
        insert_gfx(f, FONT1_BLOCK[0], FONT1_BLOCK[0] + (16 * 8 * 3), translation_path, 'gfx_exp_font1.bin')
        insert_gfx(f, FONT1_VWF_TABLE[0], FONT1_VWF_TABLE[0] + 16, translation_path, 'gfx_exp_vwf1.bin')
        insert_gfx(f, FONT2_BLOCK[0], FONT2_BLOCK[0] + (16 * 8 * 3), translation_path, 'gfx_exp_font2.bin')
        insert_gfx(f, FONT2_VWF_TABLE[0], FONT2_VWF_TABLE[0] + 16, translation_path, 'gfx_exp_vwf2.bin')

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump', help='Execute DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.set_defaults(func=soe_dumper)
b_parser = subparsers.add_parser('insert', help='Execute INSERTER')
b_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
b_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
b_parser.add_argument('-m1', '--misc1', action='store', dest='misc_file1', help='MISC filename')
b_parser.set_defaults(func=soe_inserter)
c_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
c_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
c_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
c_parser.set_defaults(func=soe_gfx_dumper)
d_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
d_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
d_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
d_parser.set_defaults(func=soe_gfx_inserter)
args = parser.parse_args()
args.func(args)
