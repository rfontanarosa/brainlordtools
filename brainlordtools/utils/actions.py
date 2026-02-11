__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

from compression import zlib
import os
import shutil
import sys
from brainlordtools.utils.games import CRC_TABLE, EXPAND_TABLE
from brainlordtools.utils.parsers import GAME_PARSERS

def copy_file(source_file, dest_file):
    try:
        shutil.copy(source_file, dest_file)
        print(f"Successfully copied to {dest_file}")
    except Exception as e:
        print(f"Copy failed: {e}")
        sys.exit(1)

def crc_check(source_file, game_id):
    if game_id not in CRC_TABLE:
        print(f"Error: Game ID '{game_id}' not found in database.")
        return sys.exit(1)
    if not os.path.exists(source_file):
        print(f"Error: File '{source_file}' not found.")
        return sys.exit(1)
    expected = CRC_TABLE[game_id].upper()
    with open(source_file, 'rb') as f:
        calc_crc = format(zlib.crc32(f.read()) & 0xFFFFFFFF, '08X')
    if calc_crc != expected:
        print(f"[{game_id.upper()}] CHECKSUM FAILED!")
        print(f"Expected: {expected}, Got: {calc_crc}")
        return sys.exit(1)
    print(f"[{game_id.upper()}] Checksum Verified: {calc_crc} [OK]")
    return True

def diff_dump(source1_dump_path, source2_dump_path, destination_dump_path, game) -> None:
    parse_dump_func = GAME_PARSERS.get(game, GAME_PARSERS['default'])
    entries1 = parse_dump_func(source1_dump_path)
    entries2 = parse_dump_func(source2_dump_path)
    with open(destination_dump_path, 'w', encoding='utf-8') as f:
        for entry_id, (text2, ref2) in entries2.items():
            text1, _ = entries1.get(entry_id, (None, None))
            if text1 is None or text1 != text2:
                f.write(f"{ref2}\r\n{text2}")

def expand_file(dest_file, game_id):
    if game_id not in EXPAND_TABLE:
        print(f"Error: No expansion size defined for '{game_id}'")
        sys.exit(1)
    if not os.path.exists(dest_file):
        print(f"Error: File '{dest_file}' not found.")
        return sys.exit(1)
    target_size = EXPAND_TABLE[game_id]
    with open(dest_file, 'r+b') as f:
        f.seek(0, os.SEEK_END)
        f.write(b'\x00' * target_size)
    print(f"[{game_id.upper()}] Expanded to {target_size // 1024} KB [OK]")
    return True
