# -*- coding: utf-8 -*-

__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, shutil, csv
from collections import OrderedDict

from _rhtools.utils import *
from _rhtools.Table2 import Table

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--crc32check', action='store_true', default=False, help='Execute CRC32CHECK')
parser.add_argument('--dump', action='store_true', default=False, help='Execute DUMP')
parser.add_argument('--insert', action='store_true', default=False, help='Execute INSERTER')
parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
parser.add_argument('-d', '--dest',  action='store', dest='dest_file', required=True, help='Destination filename')
parser.add_argument('-t1', '--table1', action='store', dest='table1', required=True, help='Original table filename')
args = parser.parse_args()

execute_crc32check = args.crc32check
execute_dump = args.dump
execute_inserter = args.insert
filename = args.source_file
filename2 = args.dest_file
tablename = args.table1
dump_path = 'soe/dump'
translation_path = 'soe/translation'
misc_path = 'soe/resources'

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

table = Table(tablename)

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

def write_text(f, text, end_byte=0x00, limit=0x47712):
    new_address = f.tell()
    text = decode_text(text)
    decoded_text = table.decode(text)
    f.write(decoded_text)
    f.write(int2byte(end_byte))
    if f.tell() > limit:
        raise Exception()
    return new_address

def write_text1(f, offset, text,end_byte=0x00):
    f.seek(offset)
    text = decode_text(text)
    decoded_text = table.decode(text)
    f.write(decoded_text)
    f.write(int2byte(end_byte))

def dump_block(f):
    for block_name, block_limits in TEXT_BLOCK.iteritems():
        filename = os.path.join(dump_path, block_name + '.csv')
        with open(filename, 'wb+') as csv_file:
            csv_writer = csv.writer(csv_file)
            f.seek(block_limits[0])
            while(f.tell() < block_limits[1]):
                address = f.tell()
                text = read_text(f)
                text_encoded = table.encode(text)
                fields = [text_encoded, address, int2hex(address)]
                csv_writer.writerow(fields)

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
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            t_value = row[0].decode('utf8')
            t_address = int(row[1])
            translated_texts[t_address] = t_value
    return translated_texts

def get_translated_misc(filename):
    translated_misc = OrderedDict()
    with open(filename, 'rb') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            t_value = row[0].decode('utf8')
            if t_value:
                t_address = int(row[1], 16)
                trans_value = row[2].decode('utf8')
                if trans_value and len(trans_value) <= len(t_value):
                    translated_misc[t_address] = trans_value
    return translated_misc

def repoint(f, pointers, new_pointers, offset=0x40000):
    for p_value, p_addresses in pointers.iteritems():
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print 'NOT FOUND 1'
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                f.write(struct.pack('H', p_new_value - offset))

def repoint_npc_enemy_names(f, pointers, new_pointers, offset=0x340000):
    for p_value, p_addresses in pointers.iteritems():
        p_new_value = new_pointers.get(p_value)
        if not p_new_value:
            print 'NOT FOUND 2'
        else:
            for p_address in p_addresses:
                f.seek(p_address)
                f.write(struct.pack('H', p_new_value - offset))
                f.write(int2byte(int(0xf4)))

if execute_dump:
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(filename, 'rb') as f:
        dump_block(f)

if execute_inserter:
    with open(filename, 'rb') as f0:
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
    with open(filename2, 'r+b') as f1:
        translated_blocks = OrderedDict()
        for block_name, block_limits in TEXT_BLOCK.iteritems():
            translation_file = os.path.join(translation_path, block_name + '.csv')
            translated_blocks[block_name] = get_translated_texts(translation_file)
        # new pointers
        new_pointers = OrderedDict()
        f1.seek(0x460ae)
        for block_name, translated_texts in translated_blocks.iteritems():
            for t_address, t_value in translated_texts.iteritems():
                if block_name not in ('npc_enemy_names1', 'npc_enemy_names2'):
                    t_new_address = write_text(f1, t_value)
                    new_pointers[t_address] = t_new_address
                else:
                    t_new_address = write_text(f1, 'X')
                    new_pointers[t_address] = t_new_address
        # repointing
        for curr_pointers in (pointers0, pointers1, pointers2, pointers3, pointers4, pointers5, pointers6, pointers7, pointers8, pointers9, pointers10, pointers11, pointers12):
            repoint(f1, curr_pointers, new_pointers)
        # npc/enemies new pointers
        new_pointers = OrderedDict()
        f1.seek(0x340000)
        for block_name, translated_texts in translated_blocks.iteritems():
            if block_name in ('npc_enemy_names1', 'npc_enemy_names2'):
                for t_address, t_value in translated_texts.iteritems():
                    t_new_address = write_text(f1, t_value, limit=0x341000)
                    new_pointers[t_address] = t_new_address
        # repointing npc/enemies
        repoint_npc_enemy_names(f1, pointers13, new_pointers)
        # misc
        misc_file = os.path.join(misc_path, 'misc.csv')
        translated_misc = get_translated_misc(misc_file)
        for t_address, trans_value in translated_misc.iteritems():
            write_text1(f1, t_address, trans_value, end_byte=0x00)
