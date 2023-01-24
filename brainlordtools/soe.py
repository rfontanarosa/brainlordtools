__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, shutil, csv
from collections import OrderedDict

from rhtools3.Table import Table
from rhutils.dump import read_text, write_text, dump_binary, insert_binary
from rhutils.rom import crc32

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

POINTER_BLOCK = OrderedDict()
POINTER_BLOCK['currency_names'] = (0xf8704, 0xf870f, 3)
POINTER_BLOCK['ring'] = (0xe814c, 0xe8653, 8)
POINTER_BLOCK['alchemy_names'] = (0x45d09, 0x45d4e, 2)
POINTER_BLOCK['alchemy_descriptions'] = (0x45d51, 0x45d96, 2)
POINTER_BLOCK['alchemy_ingredient_names'] = (0x45fc5, 0x4601e, 2)
POINTER_BLOCK['weapon_descriptions'] = (0x459fa, 0x45a11, 2)
POINTER_BLOCK['status_weapons'] = (0x438e8, 0x43b04, 36)
POINTER_BLOCK['status_armors'] = (0x43b06, 0x43c96, 10)
POINTER_BLOCK['trade_goods'] = (0xcbc00, 0xcbc19, 2)
POINTER_BLOCK['charm_names'] = (0xcbc1a, 0xcbc35, 2)
POINTER_BLOCK['charm_descriptions'] = (0xcc3d0, 0xcc3eb, 2)
POINTER_BLOCK['rare_items'] = (0xcbc36, 0xcbc42, 2)
POINTER_BLOCK['rare_item_descriptions'] = (0xcc3ec, 0xcc3f7, 2)
POINTER_BLOCK['npc_enemy_names'] = (0xeb70c, 0xedf84, 74)

FONT1_BLOCK = (0x40002, 0x40C01) # 24bit - 3byte
FONT1_VWF_TABLE = (0x40C02, 0x40C81) # 127
FONT2_BLOCK = (0x40C84, 0x41883) # 24bit - 3byte
FONT2_VWF_TABLE = (0x41884, 0x41903) # 127

def encode_text(text):
    text = text.replace(u'à', '{10}')
    text = text.replace(u'è', '{11}')
    text = text.replace(u'é', '{12}')
    text = text.replace(u'ì', '{13}')
    text = text.replace(u'ò', '{14}')
    text = text.replace(u'ù', '{15}')
    text = text.replace(u'À', '{18}')
    text = text.replace(u'È', '{19}')
    text = text.replace(u'É', '{1a}')
    text = text.replace(u'Ì', '{1b}')
    text = text.replace(u'Ò', '{1c}')
    text = text.replace(u'Ù', '{1d}')
    return text

def dump_blocks(f, table, dump_path):
    for i, (block_name, block_limits) in enumerate(TEXT_BLOCK.items()):
        filename = os.path.join(dump_path, block_name + '.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(block_limits[0])
            while f.tell() < block_limits[1]:
                text_address = f.tell()
                text = read_text(f, f.tell(), end_byte=b'\x00')
                text_encoded = table.decode(text)
                fields = [hex(text_address), text_encoded]
                csv_writer.writerow(fields)

def get_pointers(f, options):
    pointers = OrderedDict()
    block_start = options[0]
    block_end = options[1]
    length = options[2]
    f.seek(block_start)
    while f.tell() < block_end:
        p_offset = f.tell()
        pointer = f.read(length)
        p_value = struct.unpack('h', pointer[:2])[0] + 0x40000
        pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_weapon_names_pointers(f):
    pointers = OrderedDict()
    for start in (0xd8c3e + 3, 0xd8e17 + 3, 0xd8fee + 3):
        f.seek(start)
        while f.tell() < (start + (112*4)):
            p_offset = f.tell()
            pointer = f.read(112)
            p_value = struct.unpack('h', pointer[:2])[0] + 0x40000
            pointers.setdefault(p_value, []).append(p_offset)
    return pointers

def get_translated_texts(filename):
    translated_texts = OrderedDict()
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            text_address = int(row['text_address'], 16)
            translated_texts[text_address] = trans
    return translated_texts

def repoint_misc(filename, f, table, next_text_address=0x360000):
    with open(filename, 'r') as csv_file:
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
                            f.write(b'\xf6')
                        elif text_address in ('0xda692', '0xda69b'):
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            f.seek(p_address)
                            f.write(new_pointer)
                            f.seek(0xda2bc)
                            f.write(b'\xf6')
                        elif text_address in ('0xdaf68', '0xdaf71'):
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            f.seek(p_address)
                            f.write(new_pointer)
                            f.seek(0xdab67)
                            f.write(b'\xf6')
                        elif text_address == '0xddef3':
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            f.seek(p_address)
                            f.write(new_pointer)
                        else:
                            new_pointer = struct.pack('H', next_text_address - 0x360000)
                            new_pointer += pointer[2:5]
                            new_pointer += b'\xf6'
                            f.seek(p_address)
                            f.write(new_pointer)
                    trans = row.get('trans2') or row.get('trans1') or row.get('text')
                    trans = encode_text(trans)
                    trans = table.encode(trans, mte_resolver=False, dict_resolver=False)
                    next_text_address = write_text(f, next_text_address, trans, end_byte=b'\x00')

def repoint(f, pointers, new_pointers, offset=0x40000):
    for i, (p_value, p_addresses) in enumerate(pointers.items()):
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print('NOT FOUND 1')
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                f.write(struct.pack('H', p_new_value - offset))

def repoint_npc_enemy_names(f, pointers, new_pointers, offset=0x340000):
    for i, (p_value, p_addresses) in enumerate(pointers.items()):
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print('NOT FOUND 2')
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                f.write(struct.pack('H', p_new_value - offset))
                f.write(b'\xf4')

def soe_misc_dumper(args):
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

def soe_misc_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    translation_path = args.translation_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    with open(source_file, 'rb') as f0:
        p_currency_names = get_pointers(f0, POINTER_BLOCK['currency_names'])
        p_ring = get_pointers(f0, POINTER_BLOCK['ring'])
        p_alchemy_names = get_pointers(f0, POINTER_BLOCK['alchemy_names'])
        p_alchemy_descriptions = get_pointers(f0, POINTER_BLOCK['alchemy_descriptions'])
        p_alchemy_ingredient_names = get_pointers(f0, POINTER_BLOCK['alchemy_ingredient_names'])
        p_weapon_names = get_weapon_names_pointers(f0)
        p_weapon_descriptions = get_pointers(f0, POINTER_BLOCK['weapon_descriptions'])
        p_status_weapons = get_pointers(f0, POINTER_BLOCK['status_weapons'])
        p_status_armors = get_pointers(f0, POINTER_BLOCK['status_armors'])
        p_trade_goods = get_pointers(f0, POINTER_BLOCK['trade_goods'])
        p_charm_names = get_pointers(f0, POINTER_BLOCK['charm_names'])
        p_charm_descriptions = get_pointers(f0, POINTER_BLOCK['charm_descriptions'])
        p_rare_items = get_pointers(f0, POINTER_BLOCK['rare_items'])
        p_rare_item_descriptions = get_pointers(f0, POINTER_BLOCK['rare_item_descriptions'])
        p_npc_enemy_names = get_pointers(f0, POINTER_BLOCK['npc_enemy_names'])
    with open(dest_file, 'r+b') as f1:
        translated_blocks = OrderedDict()
        for i, (block_name, block_limits) in enumerate(TEXT_BLOCK.items()):
            translation_file = os.path.join(translation_path, block_name + '.csv')
            translated_blocks[block_name] = get_translated_texts(translation_file)
        # new pointers
        new_pointers = OrderedDict()
        t_new_address = 0x460ae
        for i, (block_name, translated_texts) in enumerate(translated_blocks.items()):
            for i, (t_address, t_value) in enumerate(translated_texts.items()):
                new_pointers[t_address] = t_new_address
                t_value = encode_text(t_value)
                t_value = table.encode(t_value, mte_resolver=False, dict_resolver=False)
                if block_name not in ('npc_enemy_names1', 'npc_enemy_names2'):
                    t_new_address = write_text(f1, t_new_address, t_value, end_byte=b'\x00', limit=0x47712)
                else:
                    t_new_address = write_text(f1, t_new_address, str.encode('X'), end_byte=b'\x00', limit=0x47712)
        # repointing
        repoint(f1, p_currency_names, new_pointers)
        repoint(f1, p_ring, new_pointers)
        repoint(f1, p_alchemy_names, new_pointers)
        repoint(f1, p_alchemy_descriptions, new_pointers)
        repoint(f1, p_alchemy_ingredient_names, new_pointers)
        repoint(f1, p_weapon_names, new_pointers)
        repoint(f1, p_weapon_descriptions, new_pointers)
        repoint(f1, p_status_weapons, new_pointers)
        repoint(f1, p_status_armors, new_pointers)
        repoint(f1, p_trade_goods, new_pointers)
        repoint(f1, p_charm_names, new_pointers)
        repoint(f1, p_charm_descriptions, new_pointers)
        repoint(f1, p_rare_items, new_pointers)
        repoint(f1, p_rare_item_descriptions, new_pointers)
        # npc/enemies new pointers
        new_pointers = OrderedDict()
        t_new_address = 0x340000
        for i, (block_name, translated_texts) in enumerate(translated_blocks.items()):
            if block_name in ('npc_enemy_names1', 'npc_enemy_names2'):
                for i, (t_address, t_value) in enumerate(translated_texts.items()):
                    new_pointers[t_address] = t_new_address
                    t_value = encode_text(t_value)
                    t_value = table.encode(t_value, mte_resolver=False, dict_resolver=False)
                    t_new_address = write_text(f1, t_new_address, t_value, end_byte=b'\x00')
        # repointing npc/enemies
        repoint_npc_enemy_names(f1, p_npc_enemy_names, new_pointers)

def soe_custom_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    translation_path = args.translation_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    with open(dest_file, 'r+b') as f1:
        custom_file = os.path.join(translation_path, 'misc.csv')
        repoint_misc(custom_file, f1, table)

def soe_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[1] - (16 * 8 * 3), dump_path, 'gfx_font1.bin')
        dump_binary(f, FONT1_VWF_TABLE[0], FONT1_VWF_TABLE[1] - 16, dump_path, 'gfx_vwf1.bin')
        dump_binary(f, FONT2_BLOCK[0], FONT2_BLOCK[1] - (16 * 8 * 3), dump_path, 'gfx_font2.bin')
        dump_binary(f, FONT2_VWF_TABLE[0], FONT2_VWF_TABLE[1] - 16, dump_path, 'gfx_vwf2.bin')
        dump_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[0] + (16 * 8 * 3), dump_path, 'gfx_exp_font1.bin')
        dump_binary(f, FONT1_VWF_TABLE[0], FONT1_VWF_TABLE[0] + 16, dump_path, 'gfx_exp_vwf1.bin')
        dump_binary(f, FONT2_BLOCK[0], FONT2_BLOCK[0] + (16 * 8 * 3), dump_path, 'gfx_exp_font2.bin')
        dump_binary(f, FONT2_VWF_TABLE[0], FONT2_VWF_TABLE[0] + 16, dump_path, 'gfx_exp_vwf2.bin')

def soe_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        f.seek(0xC9ED8)
        f.write(b'\x10')
        f.seek(0xCA54F)
        f.write(b'\x10')
        f.seek(0xCA5A4)
        f.write(b'\x10')
        f.seek(0xCA92A)
        f.write(b'\x10')
        f.seek(0xCB9B8)
        f.write(b'\x10')
        f.seek(0xCB9FD)
        f.write(b'\x10')
        f.seek(0xCBB21)
        f.write(b'\x10')
        f.seek(0xCC951)
        f.write(b'\x10')
        #
        f.seek(0xC9E8B)
        f.write(b'\xa9')
        f.write(b'\x71')
        f.seek(0xCA492)
        f.write(b'\xa9')
        f.write(b'\x71')
        #
        f.seek(0x129917)
        f.write(b'\x18')
        #
        insert_binary(f, FONT1_BLOCK[0] + (16 * 8 * 3), FONT1_BLOCK[1], translation_path, 'gfx_font1.bin')
        insert_binary(f, FONT1_VWF_TABLE[0] + 16, FONT1_VWF_TABLE[1], translation_path, 'gfx_vwf1.bin')
        insert_binary(f, FONT2_BLOCK[0] + (16 * 8 * 3), FONT2_BLOCK[1], translation_path, 'gfx_font2.bin')
        insert_binary(f, FONT2_VWF_TABLE[0] + 16, FONT2_VWF_TABLE[1], translation_path, 'gfx_vwf2.bin')
        insert_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[0] + (16 * 8 * 3), translation_path, 'gfx_exp_font1.bin')
        insert_binary(f, FONT1_VWF_TABLE[0], FONT1_VWF_TABLE[0] + 16, translation_path, 'gfx_exp_vwf1.bin')
        insert_binary(f, FONT2_BLOCK[0], FONT2_BLOCK[0] + (16 * 8 * 3), translation_path, 'gfx_exp_font2.bin')
        insert_binary(f, FONT2_VWF_TABLE[0], FONT2_VWF_TABLE[0] + 16, translation_path, 'gfx_exp_vwf2.bin')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMPER')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=soe_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=soe_misc_inserter)
insert_custom_parser = subparsers.add_parser('insert_custom', help='Execute CUSTOM INSERTER')
insert_custom_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_custom_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_custom_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_custom_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_custom_parser.set_defaults(func=soe_custom_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=soe_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=soe_gfx_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
