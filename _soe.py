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
dump_path = 'soe/dump/'

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

POINTERS = {
    'ring': (0xe814c, 0xe8653)
}

table = Table(tablename)

def read_text(f, end_byte=0x00):
    text = b''
    byte = b'1'
    while not byte2int(byte) == end_byte:
        byte = f.read(1)
        if byte2int(byte) != end_byte:
            text += byte
    return text

def write_text(f, text, end_byte=0x00):
    new_address = f.tell()
    decoded_text = table.decode(text)
    f.write(decoded_text)
    f.write(int2byte(end_byte))
    return new_address

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
        pointers[p_value] = p_offset
    return pointers

def get_weapons_pointers(f):
    pointers = OrderedDict()
    for start in (0xd8c3e, 0xd8e17, 0xd8fee):
        f.seek(start)
        while(f.tell() < start + (112*4)):
            p_offset = f.tell()
            pointer = f.read(112)
            p_value = string_address2int_address(pointer[3:5], switch=True, offset=0x40000)
            pointers[p_value] = p_offset
            print int2hex(p_value)
    return pointers

def repoint_ring(f, pointers, new_pointers, offset=0x40000):
    for p_value, p_address in pointers.iteritems():
        p_new_value = new_pointers.get(p_value)
        f.seek(p_address)
        f.write(struct.pack('H', p_new_value - offset))

def get_translated_texts():
    translated_texts = OrderedDict()
    for block_name, block_limits in TEXT_BLOCK.iteritems():
        filename = os.path.join(dump_path, block_name + '.csv')
        with open(filename, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                t_value = row[0]
                t_address = int(row[1])
                translated_texts[t_address] = t_value
    return translated_texts

if execute_dump:
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(filename, 'rb') as f:
        dump_block(f)


"""
pointers = where was the text => where is the pointer
new_pointers = where was the text => where is the text now
"""

if execute_inserter:
    with open(filename, 'rb') as f:
        pointers = get_ring_pointers(f)
        pointers1 = get_weapons_pointers(f)
    with open(filename2, 'r+b') as f:
        #
        new_pointers = OrderedDict()
        translated_texts = get_translated_texts()
        f.seek(0x460AE)
        for t_address, t_value in translated_texts.iteritems():
            t_new_address = write_text(f, t_value)
            new_pointers[t_address] = t_new_address
        #
        repoint_ring(f, pointers, new_pointers)
