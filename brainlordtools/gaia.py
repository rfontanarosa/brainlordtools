__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, re, shutil, sqlite3, struct, sys

from rhtools3.Table import Table
from rhutils.db import insert_text, select_translation_by_author, select_most_recent_translation
from rhutils.dump import get_csv_translated_texts, read_dump, fill
from rhutils.rom import crc32, expand_rom
from rhutils.snes import pc2snes_hirom, snes2pc_hirom
from quintettools.quintet_comp import compress as quintet_compress
from quintettools.quintet_decomp import decompress as quintet_decompress

CRC32 = '1C3848C0'

EXP_SIZE = 0x80000

pointers_offsets_to_exclude = (0x5c94, 0x64e1c, 0xa0f3e, 0xaf75e, 0xdbdc, 0x11318, 0xd2ebc, 0x13321, 0x329b9, 0x80f93, 0xbe1ec, 0xba2dc, 0xba4f3, 0x80f93, 0xaedf9, 0xa468b, 0x226ab, 0x31732, 0xd3016, 0xdd242, 0xdd244, 0xdf92a, 0xe7728, 0xe7e76, 0xf3496, 0x1032df, 0x103c2a, 0x10d8c7, 0x118258, 0x12846b, 0x12b8f4, 0x13c9dd, 0x13f292, 0x14bd72, 0x151bc7, 0x1527eb, 0x15637d, 0x16c614, 0x16c61e, 0x171027, 0x184e15, 0x188d3b, 0x1909f0, 0x19853c, 0x1ddd09, 0x1e6886, 0x1ebcf8, 0x1edec7, 0x1f0973, 0x1f0b8b, 0x1f0bcb, 0x1f189b, 0x1f8cb2, 0x1f8e28, 0x1f9e90)

locations_text_offsets = (0xc8216, 0xc831e, 0xc8357, 0xc8382, 0xc83bb, 0xc83ed, 0xc8450, 0xc84b5, 0xc8601, 0xc866e, 0xc8749, 0xc8b56, 0xc8b98, 0xc8c23, 0xc8cb2, 0xc8d7d, 0xc968b, 0xc9700, 0xc9829, 0xc9913, 0xc9bed, 0xc9cd6, 0xc9d38, 0xc9da8, 0xc9e87, 0xc9f47, 0xca00f, 0xca0bf, 0xca187, 0xca23b, 0xca32a, 0xca42f, 0xca7ea, 0xcab3e, 0xcad90, 0Xcaea8, 0xcb295, 0xcb569, 0xcb626, 0xcb836, 0xcbf5b, 0xcbfcc, 0xcc008, 0xcc03d, 0xcc182, 0xcc213, 0xccbc6, 0xccc92, 0xccffe, 0xcd080, 0xcd188, 0xcd1ea, 0xcd28f, 0xcd32f, 0xcd387, 0xcd446, 0xcd584, 0xce1fa, 0xce3e3, 0xce401, 0xce41f, 0xce43d, 0xce45b, 0xce54e)

intro_pointers_offsets = (0x0BCA80, 0x0BCAA2, 0x0BCB7E, 0x0BCBA8, 0x0BCBD2, 0x0BCBFC, 0x0BCC1F, 0x0BCDD9, 0x0BCE50, 0x0BCE8E)

credits_pointers_offsets = (0x9E9DD, 0x09E9E9, 0x09E9F5, 0x09EA01, 0x09EA0D, 0x09EA19, 0x09EA25, 0x09EA31, 0x09EA3D, 0x09EA49, 0x09EA55, 0x09EA61, 0x09EA6D, 0x09EA79, 0x09EA85, 0x09EA91, 0x09EA9D, 0x09EAA9, 0x09EAB5, 0x09EAC1, 0x09EACD, 0x09EAD9, 0x09EAE5, 0x09EAF1, 0x09EAFD, 0x09EB09, 0x09EB15, 0x09EB21, 0x09EB2D, 0x09EB42)

initial_menu_pointers_offsets = (0xbe2b5, 0xbe359, 0xbe72b, 0xbe72f, 0xbe733, 0xbe8df, 0xbea5a, 0xbebad, 0xbebd1, 0xbebf5, 0xbf6ad, 0xbf6af, 0xbf6b1)

cmd_list = {b'\xc1': 2, b'\xc3': 1, b'\xc5': 4, b'\xc6': 4, b'\xc7': 2, b'\xc9': 1, b'\xcd': 3, b'\xd1': 2, b'\xd2': 1, b'\xd5': 1, b'\xd6': 1, b'\xd7': 1, b'\xd8': 1}

TEXTS_CONFIGS = ({
    'name': 'Attacks',
    'filename': 'dump_attacks_eng.txt',
    'pointers_offsets': tuple(range(0x8eb8f, 0x8eb9b, 2)) + tuple(range(0x8ebd3, 0x8ebdf, 2)),
    'end_byte': (b'\xc0', b'\xca'),
    'append_end_byte': True,
    'tablename': 'main',
    'mte_resolver': True,
    'dict_resolver': True
}, {
    'name': 'Intro',
    'filename': 'dump_intro_eng.txt',
    'pointers_offsets': intro_pointers_offsets,
    'end_byte': b'\xca',
    'append_end_byte': False,
    'tablename': 'intro',
    'mte_resolver': False,
    'dict_resolver': False
}, {
    'name': 'Menu locations',
    'filename': 'dump_menu_locations_eng.txt',
    'pointers_offsets': range(0xbf706, 0xbf906, 2),
    'end_byte': b'\xca',
    'append_end_byte': True,
    'tablename': 'main',
    'mte_resolver': True,
    'dict_resolver': True,
    'custom_after_read_text': True
}, {
#     'name': 'Menu',
#     'filename': 'dump_menu_eng_.txt',
#     'pointers_offsets': initial_menu_pointers_offsets,
#     'end_byte': (b'\xc0', b'\xca'),
#     'append_end_byte': True,
#     'tablename': 'main',
#     'mte_resolver': True,
#     'dict_resolver': True
# }, {
    'name': 'Other text',
    'filename': 'dump_other_text_eng.txt',
    'pointers_offsets': range(0x1fd24, 0x1fda3, 2),
    'end_byte': (b'\xc0', b'\xca'),
    'append_end_byte': True,
    'tablename': 'main',
    'mte_resolver': True,
    'dict_resolver': True
})

MISCS_CONFIGS = ({
    'name': 'Credits',
    'filename': 'credits.csv',
    'pointers_offsets': credits_pointers_offsets,
    'end_byte': b'\xc0',
    'append_end_byte': False,
    'tablename': 'main',
    'mte_resolver': False,
    'dict_resolver': False
}, {
    'name': 'Dictionary 1',
    'filename': 'dictionary1.csv',
    'pointers_offsets': range(0x1eba8, 0x1eda7, 2),
    'end_byte': b'\xca',
    'append_end_byte': False,
    'tablename': 'main',
    'mte_resolver': False,
    'dict_resolver': False
}, {
    'name': 'Dictionary 2',
    'filename': 'dictionary2.csv',
    'pointers_offsets': range(0x1f54d, 0x1f6dc, 2),
    'end_byte': b'\xca',
    'append_end_byte': False,
    'tablename': 'main',
    'mte_resolver': False,
    'dict_resolver': False
}, {
    'name': 'Locations',
    'filename': 'locations.csv',
    'texts_offsets': locations_text_offsets,
    'end_byte': (b'\xc0', b'\xca'),
    'append_end_byte': False,
    'tablename': 'main',
    'mte_resolver': False,
    'dict_resolver': True
}, {
    'name': 'Misc 1',
    'filename': 'misc1.csv',
    'pointers_offsets': range(0x1dabf, 0x1db3e, 2),
    'end_byte': b'\x00',
    'append_end_byte': False,
    'tablename': 'menu',
    'mte_resolver': True,
    'dict_resolver': True
}, {
    'name': 'Misc 2',
    'filename': 'misc2.csv',
    'pointers_offsets': range(0x1de1e, 0x1de9e, 2),
    'end_byte': b'\x00',
    'append_end_byte': False,
    'tablename': 'menu',
    'mte_resolver': True,
    'dict_resolver': True
}, {
    'name': 'Misc 3',
    'filename': 'misc3.csv',
    'pointers_offsets': range(0x1e132, 0x1e184, 2),
    'end_byte': b'\x00',
    'append_end_byte': False,
    'tablename': 'menu',
    'mte_resolver': True,
    'dict_resolver': True
}, {
    'name': 'Misc 4',
    'filename': 'misc4.csv',
    'pointers_offsets': range(0x1e5ee, 0x1e603, 2),
    'end_byte': b'\x00',
    'append_end_byte': False,
    'tablename': 'menu',
    'mte_resolver': True,
    'dict_resolver': True
}, {
    'name': 'Misc 5',
    'filename': 'misc5.csv',
    'pointers_offsets': range(0x1e65f, 0x1e674, 2),
    'end_byte': b'\x00',
    'append_end_byte': False,
    'tablename': 'menu',
    'mte_resolver': True,
    'dict_resolver': True
}, {
    'name': 'Misc 6',
    'filename': 'misc6.csv',
    'pointers_offsets': range(0x1e6de, 0x1e6f5, 2),
    'end_byte': b'\x00',
    'append_end_byte': False,
    'tablename': 'menu',
    'mte_resolver': True,
    'dict_resolver': True
}, {
    'name': 'Misc 7',
    'filename': 'misc7.csv',
    'pointers_offsets': range(0x1e7ce, 0x1e7d5, 2),
    'end_byte': b'\x00',
    'append_end_byte': False,
    'tablename': 'menu',
    'mte_resolver': True,
    'dict_resolver': True
}, {
    'name': 'World Map Locations',
    'filename': 'world_map_locations.csv',
    'pointers_offsets': range(0x3b1d5, 0x3b244, 3),
    'end_byte': b'\xca',
    'append_end_byte': False,
    'tablename': 'intro',
    'mte_resolver': False,
    'dict_resolver': False
})

def gaia_read_text(f, offset=None, length=None, end_byte=None, cmd_list=None, append_end_byte=False):
    text = b''
    if offset is not None:
        f.seek(offset)
    if length:
        text = f.read(length)
    elif end_byte:
        while True:
            byte = f.read(1)
            if cmd_list and byte in cmd_list.keys():
                bytes_to_read = cmd_list.get(byte)
                read_bytes = f.read(bytes_to_read)
                if byte == b'\xd1':
                    bank_byte = f.tell() & 0xff0000
                    offset = read_bytes[0] + (read_bytes[1] << 8) + bank_byte
                    f.seek(offset)
                elif byte == b'\xcd':
                    offset_snes = (read_bytes[2] << 16) | (read_bytes[1] << 8) | read_bytes[0]
                    offset_pc = snes2pc_hirom(offset_snes)
                    current_offset = f.tell()
                    text += gaia_read_text(f, offset=offset_pc, end_byte=end_byte, cmd_list=cmd_list)
                    f.seek(current_offset)
                elif byte == b'\xd8':
                    text += byte
                    while True:
                        byte = f.read(1)
                        text += byte
                        if byte == b'\x00':
                            break
                else:
                    text += byte + read_bytes
            elif byte in end_byte:
                if append_end_byte:
                    text += byte
                break
            else:
                text += byte
    return text

def gaia_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    table3_file = args.table3
    dump_path = args.dump_path
    db = args.database_file
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table1 = Table(table1_file)
    table3 = Table(table3_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        id = 1
        pointers = {}
        pointer_offsets = [m.start() for m in re.finditer(b'\x02\xbf', f.read())]
        for pointer_offset in pointer_offsets:
            if pointer_offset in pointers_offsets_to_exclude:
                continue
            f.seek(pointer_offset)
            pointer = f.read(4)[2:]
            bank_byte = pointer_offset & 0xff0000
            text_offset = pointer[0] + (pointer[1] << 8) + bank_byte
            pointers.setdefault(text_offset, []).append(pointer_offset)
        f.seek(0)
        pointer_offsets = [m.start() for m in re.finditer(b'\x02\x19\x17', f.read())]
        for pointer_offset in pointer_offsets:
            if pointer_offset in pointers_offsets_to_exclude:
                continue
            f.seek(pointer_offset)
            pointer = f.read(5)[3:]
            bank_byte = pointer_offset & 0xff0000
            text_offset = pointer[0] + (pointer[1] << 8) + bank_byte
            pointers.setdefault(text_offset, []).append(pointer_offset)
        pointers[0x1ff02] = []
        pointers[0x1ff1f] = []
        pointers[0x1ff36] = []
        pointers[0x1ff48] = []
        pointers[0x1cb66] = []
        for i, (text_offset, pointers_offsets) in enumerate(pointers.items()):
            text = gaia_read_text(f, text_offset, end_byte=(b'\xc0', b'\xca'), cmd_list=cmd_list, append_end_byte=True)
            text_decoded = table1.decode(text, mte_resolver=True, dict_resolver=True)
            pointers_offsets_str = ';'.join(hex(x) for x in pointers_offsets)
            ref = f'[BLOCK {id}: {hex(text_offset)} to {hex(f.tell() - 1)} - {pointers_offsets_str}]'
            # dump - db
            # insert_text(cur, id, text, text_decoded, text_offset, '', 1, ref)
            # dump - txt
            filename = os.path.join(dump_path, 'dump_eng.txt')
            with open(filename, 'a+', encoding='utf-8') as out:
                out.write(f'{ref}\n{text_decoded}\n\n')
            id += 1
        # Menu
        id = 1
        pointers = {}
        pointers[0xbf3f4] = []
        pointers[0xbf437] = []
        pointers[0xbf476] = []
        pointers[0xbf48c] = []
        pointers[0xbf4a7] = []
        # pointers[0xbf4c3] = []
        # pointers[0xbf4ea] = []
        # pointers[0xbf511] = []
        pointers[0xbf538] = []
        pointers[0xbf5ad] = []
        pointers[0xbf679] = []
        pointers[0xbf6b3] = []
        pointers[0xbf6df] = []
        pointers[0xbf6ec] = []
        pointers[0xbf6f9] = []
        for _, (text_offset, pointers_offsets) in enumerate(pointers.items()):
            text = gaia_read_text(f, text_offset, end_byte=(b'\xc0', b'\xca'), cmd_list=cmd_list, append_end_byte=True)
            text_decoded = table1.decode(text, mte_resolver=True, dict_resolver=True)
            pointers_offsets_str = ';'.join(hex(x) for x in pointers_offsets)
            ref = f'[BLOCK {id}: {hex(text_offset)} to {hex(f.tell() - 1)} - {pointers_offsets_str}]'
            # dump - db
            # insert_text(cur, id, text, text_decoded, text_offset, '', 2, ref)
            # dump - txt
            filename = os.path.join(dump_path, 'dump_menu_eng.txt')
            with open(filename, 'a+', encoding='utf-8') as out:
                out.write(f'{ref}\n{text_decoded}\n\n')
            id += 1
        #
        for config in TEXTS_CONFIGS:
            _, filename, pointers_offsets, texts_offsets = config['name'], config['filename'], config.get('pointers_offsets'), config.get('texts_offsets')
            end_byte, append_end_byte = config['end_byte'], config['append_end_byte']
            tablename, mte_resolver, dict_resolver = config['tablename'], config['mte_resolver'], config['dict_resolver']
            custom_after_read_text = config.get('custom_after_read_text')
            table = table1 if tablename == 'main' else table3
            filepath = os.path.join(dump_path, filename)
            #
            id = 1
            pointers = {}
            for pointer_offset in pointers_offsets:
                f.seek(pointer_offset)
                pointer = f.read(2)
                bank_byte = pointer_offset & 0xff0000
                text_offset = pointer[0] + (pointer[1] << 8) + bank_byte
                pointers.setdefault(text_offset, []).append(pointer_offset)
            for _, (text_offset, pointers_offsets_list) in enumerate(pointers.items()):
                text = gaia_read_text(f, text_offset, end_byte=end_byte, cmd_list=cmd_list, append_end_byte=append_end_byte)
                if custom_after_read_text:
                    text += f.read(4)
                text_decoded = table.decode(text, mte_resolver=mte_resolver, dict_resolver=dict_resolver)
                pointers_offsets_str = ';'.join(hex(x) for x in pointers_offsets_list)
                ref = f'[BLOCK {id}: {hex(text_offset)} to {hex(f.tell() - 1)} - {pointers_offsets_str}]'
                # dump - db
                # insert_text(cur, id, text, text_decoded, text_address, '', 2, ref)
                # dump - txt
                with open(filepath, 'a+', encoding='utf-8') as out:
                    out.write(f'{ref}\n{text_decoded}\n\n')
                id += 1
    cur.close()
    conn.commit()
    conn.close()

def gaia_misc_dumper(args):
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
    with open(source_file, 'rb') as f:
        for config in MISCS_CONFIGS:
            _, filename, pointers_offsets, texts_offsets = config['name'], config['filename'], config.get('pointers_offsets'), config.get('texts_offsets')
            end_byte, append_end_byte = config['end_byte'], config['append_end_byte']
            tablename, mte_resolver, dict_resolver = config['tablename'], config['mte_resolver'], config['dict_resolver']
            table = table1 if tablename == 'main' else table2 if tablename == 'menu' else table3
            filepath = os.path.join(dump_path, filename)
            with open(filepath, 'w+', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                if pointers_offsets:
                    csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
                    for pointer_offset in pointers_offsets:
                        f.seek(pointer_offset)
                        pointer_value = f.read(2)
                        bank_byte = pointer_offset & 0xff0000
                        text_offset = pointer_value[0] + (pointer_value[1] << 8) + bank_byte
                        text = gaia_read_text(f, text_offset, end_byte=end_byte, cmd_list=cmd_list, append_end_byte=append_end_byte)
                        text_decoded = table.decode(text, mte_resolver=mte_resolver, dict_resolver=dict_resolver)
                        fields = [hex(pointer_offset), hex(text_offset), text_decoded]
                        csv_writer.writerow(fields)
                elif texts_offsets:
                    csv_writer.writerow(['text_address', 'text', 'trans'])
                    for text_offset in locations_text_offsets:
                        text = gaia_read_text(f, text_offset, end_byte=end_byte, cmd_list=cmd_list, append_end_byte=append_end_byte)
                        text_decoded = table.decode(text, mte_resolver=mte_resolver, dict_resolver=dict_resolver)
                        fields = [hex(text_offset), text_decoded]
                        csv_writer.writerow(fields)

def gaia_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    # Worlmap - Tileset, Tilemap arrangement, Tilemap data
    with open(source_file, 'rb') as f:
        rom = f.read()
        files = (('worldmap_tileset.bin', 0x10_000), ('worldmap_tilemap_arrangement.bin', 0x135_e1b), ('worldmap_tilemap_data.bin', 0x1a4_66e))
        for filename, offset in files:
            decompressed_data = quintet_decompress(rom, offset)
            decomp, _ = decompressed_data
            with open(os.path.join(dump_path, filename), 'wb') as out:
                out.write(decomp)
    with open(os.path.join(dump_path, 'worldmap_tilemap_arrangement.bin'), 'rb') as f1, open(os.path.join(dump_path, 'worldmap_tilemap_data.bin'), 'rb') as f2:
        tilemap = merge_tilemap(f1.read(), f2.read())
        with open(os.path.join(dump_path, 'worldmap_tilemap.bin'), 'wb') as out:
            out.write(tilemap)
    # Intro
    with open(source_file, 'rb') as f:
        rom = f.read()
        files = (('117325_intro.bin', 0x117325),)
        for filename, offset in files:
            decompressed_data = quintet_decompress(rom, offset)
            decomp, _ = decompressed_data
            with open(os.path.join(dump_path, filename), 'wb') as out:
                out.write(decomp)

def gaia_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table2_file = args.table2
    table3_file = args.table3
    translation_path = args.translation_path
    db = args.database_file
    user_name = args.user
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table2_file)
    table3 = Table(table3_file)
    #
    # buffer = dict()
    # conn = sqlite3.connect(db)
    # conn.text_factory = str
    # cur = conn.cursor()
    # rows = select_most_recent_translation(cur, ['1'])
    # for row in rows:
    #     _, _, text_decoded, _, _, translation, _, _, ref = row
    #     splitted_line = ref.split(' ')
    #     block = int(splitted_line[1].replace(':', ''))
    #     offset_from = int(splitted_line[2], 16)
    #     offset_to = int(splitted_line[4].replace(']', ''), 16)
    #     buffer[block] = ['', [offset_from, offset_to]]
    #     text = translation if translation else text_decoded
    #     buffer[block][0] = text + '\n\n'
    # cur.close()
    # conn.commit()
    # conn.close()
    #
    translation_file = os.path.join(translation_path, 'dump_ita.txt')
    dump = read_dump(translation_file)
    with open(dest_file, 'rb+') as f:
        offsets_list = []
        new_offset = 0x208_000
        f.seek(new_offset)
        for block_id, value in dump.items():
            if block_id in (1165, 1166, 1328, 1329, 1132, 1289):
                continue
            text, offsets, _ = value
            original_text_offset, _ = offsets
            encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
            if len(encoded_text) < 5:
                continue
            if f.tell() + len(encoded_text) > new_offset + 0x8_000:
                new_offset += 0x10_000
                if new_offset > 0x258_000:
                    sys.exit('Text size exceeds!')
                f.seek(new_offset)
            offsets_list.append((block_id, original_text_offset, f.tell(), encoded_text[-1]))
            f.write(encoded_text[:-1] + b'\xca')
        for block_id, original_text_offset, new_text_offset, end_byte in offsets_list:
            snes_offset = pc2snes_hirom(new_text_offset) - 0x400_000
            new_pointer_value = struct.pack('<I', snes_offset)[:3]
            f.seek(original_text_offset)
            f.write(b'\xcd' + new_pointer_value + bytes([end_byte]))
    ###
    new_offset = 0x258_000
    translation_file_attacks = os.path.join(translation_path, 'dump_attacks_ita.txt')
    dump_attacks = read_dump(translation_file_attacks)
    with open(dest_file, 'rb+') as f:
        f.seek(new_offset)
        pointers = b''
        for block, value in list(dump_attacks.items())[:6]:
            text, _, _ = value
            pointers += struct.pack('<I', f.tell())[:2]
            encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
            f.write(encoded_text)
        pointer_offset = f.tell()
        f.write(pointers)
        #
        dialog = dump[1165]
        text, offsets, _ = dialog
        original_text_offset, _ = offsets
        encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
        c5_index = encoded_text.find(b'\xc5')
        encoded_text = encoded_text[:c5_index + 1] + struct.pack('<I', pointer_offset)[:2] + encoded_text[c5_index + 3:]
        new_text_offset = f.tell()
        end_byte = encoded_text[-1]
        f.write(encoded_text[:-1] + b'\xca')
        #
        new_offset = f.tell()
        snes_offset = pc2snes_hirom(new_text_offset) - 0x400_000
        new_pointer_value = struct.pack('<I', snes_offset)[:3]
        f.seek(original_text_offset)
        f.write(b'\xcd' + new_pointer_value + bytes([end_byte]))
        ##
        f.seek(new_offset)
        pointers = b''
        for block, value in list(dump_attacks.items())[6:]:
            text, _, _ = value
            pointers += struct.pack('<I', f.tell())[:2]
            encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
            f.write(encoded_text)
        pointer_offset = f.tell()
        f.write(pointers)
        #
        dialog = dump[1166]
        text, offsets, _ = dialog
        original_text_offset, _ = offsets
        encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
        c5_index = encoded_text.find(b'\xc5')
        encoded_text = encoded_text[:c5_index + 1] + struct.pack('<I', pointer_offset)[:2] + encoded_text[c5_index + 3:]
        new_text_offset = f.tell()
        end_byte = encoded_text[-1]
        f.write(encoded_text[:-1] + b'\xca')
        #
        new_offset = f.tell()
        snes_offset = pc2snes_hirom(new_text_offset) - 0x400_000
        new_pointer_value = struct.pack('<I', snes_offset)[:3]
        f.seek(original_text_offset)
        f.write(b'\xcd' + new_pointer_value + bytes([end_byte]))
    ###
    translation_other = os.path.join(translation_path, 'dump_other_text_ita.txt')
    dump_other = read_dump(translation_other)
    with open(dest_file, 'rb+') as f:
        f.seek(new_offset)
        pointers = b''
        for block, value in list(dump_other.items()):
            text, _, _ = value
            pointers += struct.pack('<I', f.tell())[:2]
            encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
            f.write(encoded_text)
        pointer_offset = f.tell()
        f.write(pointers)
        #
        dialog = dump[1328]
        text, offsets, _ = dialog
        original_text_offset, _ = offsets
        encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
        c5_index = encoded_text.find(b'\xc5')
        encoded_text = encoded_text[:c5_index + 1] + struct.pack('<I', pointer_offset)[:2] + encoded_text[c5_index + 3:]
        new_text_offset = f.tell()
        end_byte = encoded_text[-1]
        f.write(encoded_text[:-1] + b'\xca')
        #
        dialog = dump[1329]
        text, offsets, _ = dialog
        original_text_offset, _ = offsets
        encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
        c5_index = encoded_text.find(b'\xc5')
        encoded_text = encoded_text[:c5_index + 1] + struct.pack('<I', pointer_offset)[:2] + encoded_text[c5_index + 3:]
        new_text_offset = f.tell()
        end_byte = encoded_text[-1]
        f.write(encoded_text[:-1] + b'\xca')
        #
        new_offset = f.tell()
        snes_offset = pc2snes_hirom(new_text_offset) - 0x400_000
        new_pointer_value = struct.pack('<I', snes_offset)[:3]
        f.seek(original_text_offset)
        f.write(b'\xcd' + new_pointer_value + bytes([end_byte]))
    ###
    with open(dest_file, 'rb+') as f1, open(dest_file, 'rb+') as f2:
        new_offset = 0xbf906
        f1.seek(new_offset)
        # Menu locations
        translation_file = os.path.join(translation_path, 'dump_menu_locations_ita.txt')
        dump = read_dump(translation_file)
        for block_id, value in dump.items():
            text, _, pointer_offsets = value
            pointer_value = struct.pack('<H', f1.tell() & 0x00ffff)
            encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
            f1.write(encoded_text)
            for pointer_offset in pointer_offsets:
                f2.seek(pointer_offset)
                f2.write(pointer_value)
        # Intro
        translation_file = os.path.join(translation_path, 'dump_intro_ita.txt')
        dump = read_dump(translation_file)
        for block_id, value in dump.items():
            text, _, pointer_offsets = value
            pointer_value = struct.pack('<H', f1.tell() & 0x00ffff)
            encoded_text = table3.encode(text[:-2], mte_resolver=False, dict_resolver=False)
            f1.write(encoded_text + b'\xca')
            for pointer_offset in pointer_offsets:
                f2.seek(pointer_offset)
                f2.write(pointer_value)
        # Menu
        offsets_list = []
        translation_file = os.path.join(translation_path, 'dump_menu_ita.txt')
        dump = read_dump(translation_file)
        for block_id, value in dump.items():
            text, offsets, _ = value
            original_text_offset, _ = offsets
            encoded_text = table.encode(text[:-2], mte_resolver=True, dict_resolver=True)
            if len(encoded_text) < 5:
                continue
            offsets_list.append((block_id, original_text_offset, f1.tell(), encoded_text[-1]))
            f1.write(encoded_text[:-1] + b'\xca')
        for block_id, original_text_offset, new_text_offset, end_byte in offsets_list:
            snes_offset = pc2snes_hirom(new_text_offset) - 0x400_000
            new_pointer_value = struct.pack('<I', snes_offset)[:3]
            f2.seek(original_text_offset)
            f2.write(b'\xcd' + new_pointer_value + bytes([end_byte]))
        #
        if (f1.tell() > 0xbffff):
            sys.exit(f'Text size exceeds: {f1.tell() - 0xbffff}')

def gaia_misc_inserter(args):
    dest_file = args.dest_file
    table1_file = args.table1
    table2_file = args.table2
    table3_file = args.table3
    translation_path = args.translation_path
    table1 = Table(table1_file)
    table2 = Table(table2_file)
    table3 = Table(table3_file)
    with open(dest_file, 'r+b') as f1, open(dest_file, 'r+b') as f2:
        # Credits
        translation_file = os.path.join(translation_path, 'credits.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        f1.seek(0x9f6b0)
        for i, (pointer_offset, _, text_value) in enumerate(translated_texts):
            # pointer
            new_pointer_value = struct.pack('<H', f1.tell() & 0x00ffff)
            f2.seek(pointer_offset)
            f2.write(new_pointer_value)
            # text
            encoded_text = table1.encode(text_value, mte_resolver=False, dict_resolver=False)
            f1.write(encoded_text + b'\xc0')
            if (f1.tell() > 0x9f_fff):
                sys.exit('Text size exceeds!')
        # Dictionaries
        fill(f1, 0x1eba8, 0x1fd24 - 0x1eba8)
        # Dictionary 1
        translation_file = os.path.join(translation_path, 'dictionary1.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        new_pointers_offsets = range(0x6dce0, 0x6dce0 + 512, 2)
        f1.seek(0x6dce0 + 512)
        for i, (_, _, text_value) in enumerate(translated_texts):
            # pointer
            new_pointer_value = struct.pack('<H', f1.tell() & 0x00ffff)
            f2.seek(new_pointers_offsets[i])
            f2.write(new_pointer_value)
            # text
            encoded_text = table1.encode(text_value, mte_resolver=False, dict_resolver=False)
            f1.write(encoded_text + b'\xca')
            if (f1.tell() > 0x6ffff):
                sys.exit('Text size exceeds!')
        # Dictionary 2
        translation_file = os.path.join(translation_path, 'dictionary2.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        new_pointers_offsets = range(0x6ece0, 0x6ece0 + 402, 2)
        f1.seek(0x6ece0 + 402)
        for i, (_, text_offset, text_value) in enumerate(translated_texts):
            # pointer
            new_pointer_value = struct.pack('<H', f1.tell() & 0x00ffff)
            f2.seek(new_pointers_offsets[i])
            f2.write(new_pointer_value)
            # text
            encoded_text = table1.encode(text_value, mte_resolver=False, dict_resolver=False)
            f1.write(encoded_text + b'\xca')
            if (f1.tell() > 0x6ffff):
                sys.exit('Text size exceeds!')
        # Locations
        translation_file = os.path.join(translation_path, 'locations.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        f1.seek(0x2f_200)
        for i, (_, text_offset, text_value) in enumerate(translated_texts):
            if len(text_value) < 4:
                continue
            # jump
            snes_offset = pc2snes_hirom(f1.tell()) - 0x400_000
            new_pointer_value = struct.pack('<I', snes_offset)[:3]
            f2.seek(text_offset)
            f2.write(b'\xcd' + new_pointer_value + b'\xca')
            # text
            encoded_text = table1.encode(text_value, mte_resolver=True, dict_resolver=False)
            f1.write(encoded_text + b'\xca')
            if (f1.tell() > 0x2f_fff):
                sys.exit('Text size exceeds!')
        # Miscs
        f1.seek(0x1eba8)
        for config in MISCS_CONFIGS[4:13]:
            _, filename, _, _ = config['name'], config['filename'], config.get('pointers_offsets'), config.get('texts_offsets')
            end_byte, _ = config['end_byte'], config['append_end_byte']
            tablename, mte_resolver, dict_resolver = config['tablename'], config['mte_resolver'], config['dict_resolver']
            table = table1 if tablename == 'main' else table2 if tablename == 'menu' else table3
            filepath = os.path.join(translation_path, filename)
            translated_texts = get_csv_translated_texts(filepath)
            for i, (pointer_offset, _, text_value) in enumerate(translated_texts):
                # pointer
                new_pointer_value = struct.pack('<H', f1.tell() & 0x00ffff)
                f2.seek(pointer_offset)
                f2.write(new_pointer_value)
                # text
                encoded_text = table.encode(text_value, mte_resolver=mte_resolver, dict_resolver=dict_resolver)
                f1.write(encoded_text + end_byte)
                if (f1.tell() > 0x1fd24):
                    sys.exit('Text size exceeds!')
        # World Map Locations
        translation_file = os.path.join(translation_path, 'world_map_locations.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        f1.seek(0x3f_600)
        for i, (pointer_offset, _, text_value) in enumerate(translated_texts):
            # pointer
            new_pointer_value = struct.pack('<H', f1.tell() & 0x00ffff)
            f2.seek(pointer_offset)
            f2.write(new_pointer_value)
            # text
            encoded_text = table3.encode(text_value, mte_resolver=False, dict_resolver=False)
            f1.write(encoded_text + b'\xca')
            if (f1.tell() > 0x3f_fff):
                sys.exit('Text size exceeds!')

def gaia_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open (dest_file, 'r+b') as out:
        offset = 0x268_000
        # Font, Prologue font, Intro gfx, Intro data, Worldmap - Tileset
        files = (
            ('01146a8_font_ita.bin', [0xd8008]),
            ('196BD8_prologue_font_ita.bin', [0xd9bad, 0xdafc2]),
            ('117325_intro_ita.bin', [0xdaf1d]),
            ('1d7773_intro_data_ita.bin', [0xdaf2c]),
            ('010000_world_map_tileset_ita.bin', [0xdafa6, 0xdaeef])
        )
        for filename, pointers_offsets in files:
            snes_offset = pc2snes_hirom(offset) - 0x400_000
            new_pointer_value = struct.pack('<I', snes_offset)
            for pointer_offset in pointers_offsets:
                out.seek(pointer_offset)
                out.write(new_pointer_value[:3])
            with open(os.path.join(translation_path, filename), 'rb') as f:
                out.seek(offset)
                decompressed_data = f.read()
                compressed_data = quintet_compress(decompressed_data)
                out.write(compressed_data)
                offset = out.tell()
        # Worlmap - Tilemap
        with open (os.path.join(translation_path, 'worldmap_tilemap_ita.bin'), 'rb') as f:
            arrangement, data = split_tilemap(f.read())
            # Tilemap arrangement
            snes_offset = pc2snes_hirom(offset) - 0x400_000
            new_pointer_value = struct.pack('<I', snes_offset)
            for pointer_offset in [0xdaf04, 0xdafac]:
                out.seek(pointer_offset)
                out.write(new_pointer_value[:3])
            out.seek(offset)
            compressed_data = quintet_compress(arrangement)
            out.write(b'\x04\x04' + compressed_data)
            offset = out.tell()
            # Tilemap data
            snes_offset = pc2snes_hirom(offset) - 0x400_000
            new_pointer_value = struct.pack('<I', snes_offset)
            for pointer_offset in [0xdaeff, 0xdaf9f]:
                out.seek(pointer_offset)
                out.write(new_pointer_value[:3])
            out.seek(offset)
            compressed_data = quintet_compress(data)
            out.write(compressed_data)
            offset = out.tell()

def gaia_expander(args):
    dest_file = args.dest_file
    expand_rom(dest_file, EXP_SIZE)

#####

TOTAL_SIZE = 128 * 128  # Total map size
BLOCK_HEIGHT = 32       # Height of each horizontal strip
SECTION_WIDTH = 32      # Width of each section within a strip
TILES_PER_ROW = 16      # Number of tiles processed in each inner loop

def merge_tilemap(arrangement_data, tilemap_data):
    output_data = bytearray(TOTAL_SIZE * 2)
    offset = 0
    arrangement_offset = 0

    # Process each 128x32 horizontal strip
    for block_y in range(0, TOTAL_SIZE * 2, BLOCK_HEIGHT * 128 * 2):
        # Process each 32x32 section within the strip
        for block_x in range(0, 128 * 2, SECTION_WIDTH * 2):
            # Process each row of tiles within the section
            for tile_index in range(0, BLOCK_HEIGHT * 128 * 2, 256 * 2):
                offset = block_y + block_x + tile_index

                # Process 4 tiles together in this row
                for _ in range(TILES_PER_ROW):
                    # Get tilemap data
                    tilemap_ofs = arrangement_data[arrangement_offset] * 8

                    output_data[offset]         = tilemap_data[tilemap_ofs ]
                    output_data[offset + 1]     = tilemap_data[tilemap_ofs + 1]
                    output_data[offset + 2]     = tilemap_data[tilemap_ofs + 2]
                    output_data[offset + 3]     = tilemap_data[tilemap_ofs + 3]
                    output_data[offset + 0x100] = tilemap_data[tilemap_ofs + 4]
                    output_data[offset + 0x101] = tilemap_data[tilemap_ofs + 5]
                    output_data[offset + 0x102] = tilemap_data[tilemap_ofs + 6]
                    output_data[offset + 0x103] = tilemap_data[tilemap_ofs + 7]

                    offset += 4
                    arrangement_offset += 1

    return output_data

def split_tilemap(input_data):
    # Sanity‑check input length: 128×128×2 bytes = 32 768
    if len(input_data) != TOTAL_SIZE * 2:
        raise ValueError("Converted_data must be exactly 32 768 bytes")

    # ---------- 1st step – collect unique 8‑byte sequences -------------
    unique = []
    for block_y in range(0, TOTAL_SIZE * 2, BLOCK_HEIGHT * 128 * 2):
        for block_x in range(0, 128 * 2, SECTION_WIDTH * 2):
            for tile_index in range(0, BLOCK_HEIGHT * 128 * 2, 256 * 2):
                offset = block_y + block_x + tile_index
                for _ in range(TILES_PER_ROW):
                    seq = (input_data[offset : offset + 4] + input_data[offset + 0x100: offset + 0x100 + 4])
                    if seq not in unique:
                        unique.append(seq)
                    offset += 4

    if (len(unique) > 256):
        print(f"Too many unique tiles: {len(unique)}")

    # ---------- 2nd step – build arrangement + tile‑map -------------
    output_arrangement_data = bytearray(4096)
    output_tilemap_data     = bytearray(256 * 8)
    arr_pos = 0

    for block_y in range(0, TOTAL_SIZE * 2, BLOCK_HEIGHT * 128 * 2):
        for block_x in range(0, 128 * 2, SECTION_WIDTH * 2):
            for tile_index in range(0, BLOCK_HEIGHT * 128 * 2, 256 * 2):
                offset = block_y + block_x + tile_index
                for _ in range(TILES_PER_ROW):
                    seq = (input_data[offset : offset + 4] + input_data[offset + 0x100: offset + 0x100 + 4])

                    if seq in unique:
                        index = unique.index(seq)
                    else:
                        print("Sequence not in unique")

                    base = index * 8
                    output_tilemap_data[base : base + 8] = seq

                    output_arrangement_data[arr_pos] = index

                    arr_pos += 1
                    offset += 4

    return bytes(output_arrangement_data), bytes(output_tilemap_data)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Menu table filename')
dump_text_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Intro table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=gaia_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified original table filename')
insert_text_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Modified intro table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=gaia_text_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Menu table filename')
dump_misc_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Intro table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=gaia_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Menu table filename')
insert_misc_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Intro table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=gaia_misc_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=gaia_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=gaia_gfx_inserter)
expand_parser = subparsers.add_parser('expand', help='Execute EXPANDER')
expand_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
expand_parser.set_defaults(func=gaia_expander)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
