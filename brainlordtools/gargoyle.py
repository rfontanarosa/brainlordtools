__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, struct, sys

from rhutils.dump import dump_binary, insert_binary, get_csv_translated_texts, read_text, write_text
from rhutils.rom import crc32
from rhutils.table import Table

CRC32 = '693a'

TEXT_POINTERS = (0x16000, 0x16114)
MISC_POINTERS1 = (0x16114, 0x16122)
MISC_POINTERS2 = (0x16128, 0x16208)
BANK1_LIMIT = 0x17fff

def gargoyle_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=False)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # READ POINTERS BLOCK
        start, end = TEXT_POINTERS
        pointers = {}
        f.seek(start)
        while f.tell() <= end:
            p_offset = f.tell()
            p_value = struct.unpack('H', f.read(2))[0] + 0x10000
            pointers.setdefault(p_value, []).append(p_offset)
        # READ TEXT BLOCK
        text_id = 1
        for i, (taddress, paddresses) in enumerate(list(pointers.items())[:-1]):
            pointer_addresses = ';'.join(hex(x) for x in paddresses)
            f.seek(taddress)
            next_taddress, _ = list(pointers.items())[i + 1]
            text = f.read(next_taddress - taddress)
            text_decoded = table.decode(text)
            ref = f'[ID {text_id} - TEXT {hex(taddress)} - POINTER {pointer_addresses}]'
            # dump - txt
            filename = os.path.join(dump_path, 'dump_eng.txt')
            with open(filename, 'a+', encoding='utf-8') as out:
                out.write(f'{ref}\n{text_decoded}\n\n')
            text_id += 1

def gargoyle_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    table2_file = args.table2
    table3_file = args.table3
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table1 = Table(table1_file)
    table2 = Table(table2_file)
    table3 = Table(table3_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f, open(source_file, 'rb') as f2:
        # misc1
        filename = os.path.join(dump_path, 'misc1.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
            pointers = {}
            f.seek(MISC_POINTERS1[0])
            while f.tell() < MISC_POINTERS1[1]:
                pointers[f.tell() - 2] = struct.unpack('H', f.read(2))[0] + 0x10000
            for pointer, value in pointers.items():
                f.seek(value)
                text = read_text(f, f.tell(), end_byte=b'\x75')
                text_decoded = table1.decode(text)
                fields = [hex(pointer), hex(value), text_decoded]
                csv_writer.writerow(fields)
        # misc2
        filename = os.path.join(dump_path, 'misc2.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
            pointers = {}
            f.seek(MISC_POINTERS2[0])
            while f.tell() < MISC_POINTERS2[1]:
                pointers[f.tell() - 2] = struct.unpack('H', f.read(2))[0] + 0x10000
            for pointer, value in pointers.items():
                f.seek(value)
                text = read_text(f, f.tell(), end_byte=b'\x00')
                text_decoded = table1.decode(text)
                fields = [hex(pointer), hex(value), text_decoded]
                csv_writer.writerow(fields)
        # misc3
        filename = os.path.join(dump_path, 'misc3.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
            #
            pointers = (0x829a, 0x82a6, 0x82af)
            for pointer in pointers:
                f.seek(pointer)
                text_address = struct.unpack('H', f.read(2))[0] + 0x4000
                text = read_text(f, text_address, end_byte=b'\x7f', append_end_byte=True)
                text_decoded = table2.decode(text)
                fields = [hex(pointer), hex(text_address), text_decoded]
                csv_writer.writerow(fields)
            #
            pointers = (0x853b, 0x8530)
            for pointer in pointers:
                f.seek(pointer)
                text_address = struct.unpack('H', f.read(2))[0] + 0x4000
                text = read_text(f, text_address, length=16+3)
                text_decoded = table2.decode(text)
                fields = [hex(pointer), hex(text_address), text_decoded]
                csv_writer.writerow(fields)
            #
            pointer = 0x8440
            f.seek(pointer)
            text_address = struct.unpack('H', f.read(2))[0] + 0x4000
            text = read_text(f, text_address, length=37)
            text_decoded = table2.decode(text)
            fields = [hex(pointer), hex(text_address), text_decoded]
            csv_writer.writerow(fields)
        # misc4
        filename = os.path.join(dump_path, 'misc4.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            #
            text_address = 0x187e
            for _ in range(9):
                text = read_text(f, text_address, length=7)
                text_decoded = table2.decode(text)
                fields = [hex(text_address), text_decoded]
                csv_writer.writerow(fields)
                text_address = f.tell()
        # misc5
        filename = os.path.join(dump_path, 'misc5.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            #
            for text_address in (0x32bc, 0x32cb ,0x32d0 ,0x32d5 ,0x32e2 ,0x32f1 ,0x32f6):
                text = read_text(f, text_address, length=1)
                text_decoded = table2.decode(text)
                fields = [hex(text_address), text_decoded]
                csv_writer.writerow(fields)
        # misc6
        filename = os.path.join(dump_path, 'misc6.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            #
            for text_address in (0x8058, 0x8060 ,0x8068 ,0x8070):
                text = read_text(f, text_address, length=1)
                text_decoded = table3.decode(text)
                fields = [hex(text_address), text_decoded]
                csv_writer.writerow(fields)
            #
            text_address = 0x83f2
            text = read_text(f, text_address, length=50)
            text_decoded = table3.decode(text)
            fields = [hex(text_address), text_decoded]
            csv_writer.writerow(fields)
        # misc7
        filename = os.path.join(dump_path, 'misc7.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            #
            pointers = [(0xfd74, 8), (0xfd95, 1), (0xfdd5, 4)]
            for p_offset, n in pointers:
                # 0xfd74 # puntatore a level fino a darkfire
                # 0xfd95 # puntatore ad item 1
                # 0xfda1 # puntatore ai puntatori
                # 0xfdd5 # puntatore ad item 2
                f.seek(p_offset)
                text_address = struct.unpack('H', f.read(2))[0] + 0x8000
                f.seek(text_address)
                for _ in range(n):
                    first_byte = f.read(1)
                    byte_with_length = f.read(1)
                    if byte_with_length == b'\x00':
                        first_byte += b'\x00'
                        byte_with_length = f.read(1)
                    bytes_to_read = int.from_bytes(byte_with_length, byteorder='big') & 0x0F
                    text = read_text(f, length=bytes_to_read)
                    text_decoded = table2.decode(first_byte + byte_with_length + text)
                    fields = [hex(text_address), text_decoded]
                    csv_writer.writerow(fields)
                    text_address = f.tell()
            f2.seek(0xfda1)
            pointers_address = struct.unpack('H', f2.read(2))[0] + 0x8000
            f2.seek(pointers_address)
            for _ in range(8):
                text_address = struct.unpack('H', f2.read(2))[0] + 0x8000
                f.seek(text_address)
                f.read(1)
                byte_with_length = f.read(1)
                if byte_with_length == b'\x00':
                    byte_with_length = f.read(1)
                bytes_to_read = int.from_bytes(byte_with_length, byteorder='big') & 0x0F
                text = read_text(f, length=bytes_to_read)
                text_decoded = table2.decode(b'\x00' + byte_with_length + text)
                fields = [hex(text_address), text_decoded]
                csv_writer.writerow(fields)
                text_address = f.tell()

def gargoyle_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    table2_file = args.table2
    translation_dump_path = args.translation_path1
    translation_misc_path = args.translation_path2
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table1 = Table(table1_file)
    table2 = Table(table2_file)
    #
    buffer = {}
    translation_file = os.path.join(translation_dump_path, 'dump_ita.txt')
    with open(translation_file, 'r', encoding='utf-8') as f:
        for line in f:
            if '[ID ' in line:
                splitted_line = line[1:-2].split(' ')
                block = int(splitted_line[1].replace(':', ''))
                buffer[block] = ['', splitted_line[7]]
            else:
                buffer[block][0] += line
    #
    with open(dest_file, 'r+b') as f1, open(dest_file, 'r+b') as f2:
        f1.seek(0x1647f)
        # misc1
        translation_file = os.path.join(translation_misc_path, 'misc1.csv')
        with open(translation_file, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                trans = row.get('trans') or row.get('text')
                pointer_address = int(row['pointer_address'], 16)
                #
                encoded_trans = table2.encode(trans)
                pointer_value = struct.pack('H', f1.tell() - 0x10000)
                f1.write(encoded_trans + b'\x75')
                f2.seek(pointer_address)
                f2.write(pointer_value)
        # misc2
        translation_file = os.path.join(translation_misc_path, 'misc2.csv')
        with open(translation_file, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                trans = row.get('trans') or row.get('text')
                pointer_address = int(row['pointer_address'], 16)
                #
                encoded_trans = table2.encode(trans)
                pointer_value = struct.pack('H', f1.tell() - 0x10000)
                f1.write(encoded_trans + b'\x00')
                f2.seek(pointer_address)
                f2.write(pointer_value)
        # dump
        new_text_offset = f1.tell()
        for i, (text, pointers) in buffer.items():
            for pointer in pointers.split(';'):
                pointer = int(pointer, 16)
                f1.seek(pointer)
                f1.write(struct.pack('H', new_text_offset - 0x10000))
            f1.seek(new_text_offset)
            text_to_write = table1.encode(text[:-2])
            if f1.tell() + len(text_to_write) > BANK1_LIMIT:
                sys.exit(f'ERROR: {i}')
            f1.write(text_to_write)
            new_text_offset = f1.tell()
        f1.write(b'\x00' * (BANK1_LIMIT - f1.tell()))

def gargoyle_misc_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    table2_file = args.table2
    table3_file = args.table3
    translation_path = args.translation_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table1 = Table(table1_file)
    table2 = Table(table2_file)
    table3 = Table(table3_file)
    with open(dest_file, 'r+b') as f1, open(dest_file, 'r+b') as f2:
        # misc3
        f1.seek(0x8980)
        translation_file = os.path.join(translation_path, 'misc3.csv')
        with open(translation_file, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                trans = row.get('trans') or row.get('text')
                pointer_address = int(row['pointer_address'], 16)
                #
                encoded_trans = table2.encode(trans)
                pointer_value = struct.pack('H', f1.tell() - 0x4000)
                if f1.tell() + len(encoded_trans) > 0x8d7f:
                    sys.exit(f'ERROR: {hex(0x8d7f)}')
                f1.write(encoded_trans)
                f2.seek(pointer_address)
                f2.write(pointer_value)
        # misc4
        write_text(f1, 0x17e2, b'\x08') # number of characters per line
        write_text(f1, 0x185e, b'\x08') # number of characters per line
        write_text(f1, 0x186b, b'\x08') # number of characters per line
        write_text(f1, 0x1804, b'\x08') # number of characters per line
        write_text(f1, 0x164e, b'\xad') # 0xab -> 0xad
        write_text(f1, 0x1673, b'\xad') # 0xab -> 0xad (to verify)
        write_text(f1, 0x1695, b'\xad') # 0xab -> 0xad
        write_text(f1, 0x1699, b'\xad') # 0xab -> 0xad
        write_text(f1, 0x185b, b'\x96\x38') # menu pointer address
        f1.seek(0x3896) # new menu address
        translation_file = os.path.join(translation_path, 'misc4.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for _, (_, t_value) in enumerate(translated_texts.items()):
            text = table2.encode(t_value)
            if len(text) > 8:
                sys.exit(f'{t_value} exceeds')
            f1.write(text)
        # misc5
        translation_file = os.path.join(translation_path, 'misc5.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for _, (t_address, t_value) in enumerate(translated_texts.items()):
            text = table2.encode(t_value)
            f1.seek(t_address)
            f1.write(text)
        # misc6
        translation_file = os.path.join(translation_path, 'misc6.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for _, (t_address, t_value) in enumerate(translated_texts.items()):
            text = table3.encode(t_value)
            f1.seek(t_address)
            f1.write(text)
        # misc7
        translation_file = os.path.join(translation_path, 'misc7.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        translated_items = list(translated_texts.items())
        f1.seek(0xff34)
        # 0xfd74, 8
        for _, (t_address, t_value) in enumerate(translated_items[:8]):
            text = table2.encode(t_value)
            if f1.tell() + len(text) > 0xffff:
                sys.exit('Text overflow')
            f1.write(text)
        # 0xfd95, 1
        pointer_value = struct.pack('H', f1.tell() - 0x8000)
        write_text(f2, 0xfd95, pointer_value)
        _, t_value = translated_items[8]
        text = table2.encode(t_value)
        if f1.tell() + len(text) > 0xffff:
            sys.exit('Text overflow')
        f1.write(text)
        # 0xfdd5, 4
        pointer_value = struct.pack('H', f1.tell() - 0x8000)
        write_text(f2, 0xfdd5, pointer_value)
        _, t_value = translated_items[9]
        for _, (t_address, t_value) in enumerate(translated_items[9:13]):
            text = table2.encode(t_value)
            if f1.tell() + len(text) > 0xffff:
                sys.exit('Text overflow')
            f1.write(text)
        # 0xfda1, 8
        pointer_value = struct.pack('H', f1.tell() - 0x8000)
        write_text(f2, 0xfda1, pointer_value)
        pointers_address = f1.tell() # pointers
        f1.seek(pointers_address + 16) # text
        bank_limit = 0xffff
        for i, (t_address, t_value) in enumerate(translated_items[13:]):
            text = table2.encode(t_value)
            if f1.tell() + len(text) > bank_limit:
                f1.seek(0xefb0)
                bank_limit = 0xefff
                # sys.exit('Text overflow')
            pointer_value = struct.pack('H', f1.tell() - 0x8000)
            write_text(f2, pointers_address + (i*2), pointer_value)
            f1.write(text)

def gargoyle_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, 0x18000, 0x18800, dump_path, '18000_title.bin')
        dump_binary(f, 0x14000, 0x14200, dump_path, '14000_font.bin')

def gargoyle_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, 0x18000, 0x18800, translation_path, '18000_title_ita.bin')
        # insert_binary(f, 0x14000, 0x14200, translation_path, '14000_font_ita.bin')
        insert_binary(f, 0x1c800, 0x1cba0, translation_path, '1C800_ingame_menu_ita.bin')
        write_text(f, 0x2341, b'\xa4')

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
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERT')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Modified table filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp1', '--translation_dump_path', action='store', dest='translation_path1', help='Translation DUMP path')
insert_text_parser.add_argument('-tp2', '--translation_misc_path', action='store', dest='translation_path2', help='Translation MISC path')
insert_text_parser.set_defaults(func=gargoyle_text_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Original table filename')
dump_misc_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=gargoyle_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERT')
insert_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_misc_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Original table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=gargoyle_misc_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=gargoyle_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=gargoyle_gfx_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
