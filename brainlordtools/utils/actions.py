__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import zlib
import os
import shutil
import sqlite3
import sys
import time

from brainlordtools.rhutils.db import TranslationStatus, insert_text, insert_translation, select_most_recent_translation, select_text_file_locations, select_translation_by_author
from brainlordtools.utils.games import CRC_TABLE, EXPAND_TABLE
from brainlordtools.utils.parsers import GAME_PARSERS, SMRPG_BATTLE_ID_OFFSET, parse_metadata

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

def diff_dump(source1_dump_path, source2_dump_path, destination_dump_path, game_id) -> None:
    parse_dump_func = GAME_PARSERS.get(game_id, GAME_PARSERS['default'])
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

DUMP_FILE_EXTENSIONS = ('.txt',)

def _is_dump_file(name):
    """True for the text dumps picked up when walking a dump folder.

    A dump root sits next to graphics and OS cruft (`graphics/*.png`,
    `.DS_Store`), so a walk keeps only the text dumps. Paths passed
    explicitly are never filtered.
    """
    return not name.startswith('.') and name.lower().endswith(DUMP_FILE_EXTENSIONS)

def _resolve_dump_sources(source):
    """Return (path, filename) pairs for every dump file to process.

    `filename` is the key stored in (and read from) the `texts.filename`
    column: the basename of a file given on its own, or the path relative to
    the dump root when `source` is that root, so `export_translation` can
    recreate the tree.

    `source` is either a dump root folder -- walked recursively, in name order,
    keeping only dump files -- or a single file path / list of file paths.
    """
    sources = [source] if isinstance(source, str) else list(source)
    resolved = []
    for src in sources:
        if os.path.isdir(src):
            for dirpath, dirnames, names in os.walk(src):
                dirnames[:] = sorted(d for d in dirnames if not d.startswith('.'))
                for name in sorted(names):
                    if not _is_dump_file(name):
                        continue
                    path = os.path.join(dirpath, name)
                    resolved.append((path, os.path.relpath(path, src)))
        else:
            resolved.append((src, os.path.basename(src)))
    return resolved

def import_dump(db, source_dump_path, game_id) -> None:
    parse_dump_func = GAME_PARSERS.get(game_id, GAME_PARSERS['default'])
    sources = _resolve_dump_sources(source_dump_path)
    with sqlite3.connect(db) as conn:
        conn.text_factory = str
        cur = conn.cursor()
        incremental_id = 0
        for source_path, filename in sources:
            entries = parse_dump_func(source_path)
            if not entries:
                # Folder imports pick up every .txt below the root, so say it out
                # loud when one holds nothing the parser recognises.
                print(f"Skipping {filename}: no entries parsed")
                continue
            incremental_index = 0
            for _, (text, ref) in entries.items():
                incremental_id += 1
                incremental_index += 1
                should_parse = game_id not in {'evermore', 'starocean'} and ref != ''
                metadata = parse_metadata(ref) if should_parse else {}
                text_decoded = text.strip('\r\n')
                text_address = metadata.get('START', '')
                pointer_addresses = metadata.get('POINTERS', '')
                size = metadata.get('SIZE', len(text_decoded))
                block = metadata.get('BLOCK', 1)
                dump_type = 'default' if game_id not in {'soe', 'starocean', 'smrpg'} else game_id
                file_index = metadata.get('ID', incremental_index)
                insert_text(cur, incremental_id, text_decoded, text_address, pointer_addresses, size, block, ref, dump_type, filename, file_index)

def _load_original_dumps(original_dump_path, parse_dump_func):
    """Parse the optional original dump(s) used to skip untranslated entries.

    A directory is parsed per file (keyed by the path relative to it, so nested
    dumps match too); a single file is kept under `None` so the legacy
    single-file behaviour is unchanged.
    """
    if not original_dump_path:
        return {}
    if os.path.isdir(original_dump_path):
        return {
            name: parse_dump_func(path)
            for path, name in _resolve_dump_sources(original_dump_path)
        }
    return {None: parse_dump_func(original_dump_path)}

def import_translation(db, source_dump_path, user_name, original_dump_path, game_id) -> None:
    parse_dump_func = GAME_PARSERS.get(game_id, GAME_PARSERS['default'])
    sources = _resolve_dump_sources(source_dump_path)
    with sqlite3.connect(db) as conn:
        conn.text_factory = str
        cur = conn.cursor()
        by_location, by_id = set(), {}
        for id_, filename, file_index in select_text_file_locations(cur).fetchall():
            by_location.add((filename, str(file_index)))
            by_id[str(id_)] = (filename, file_index)
        original_dumps = _load_original_dumps(original_dump_path, parse_dump_func)
        for source_path, name in sources:
            translation_dump = parse_dump_func(source_path)
            original_dump = original_dumps.get(name, original_dumps.get(None))
            for current_id, (text, _) in translation_dump.items():
                if original_dump and original_dump.get(current_id, [None])[0] == text:
                    continue
                if (name, str(current_id)) in by_location:
                    filename, file_index = name, current_id
                elif str(current_id) in by_id:
                    filename, file_index = by_id[str(current_id)]
                else:
                    print(f"Skipping {name} entry {current_id}: no matching text row")
                    continue
                insert_translation(cur, filename, file_index, user_name, text, TranslationStatus.DONE, time.time(), '', '')

def _format_export_row(row, game_id, filename=None, file_index=None) -> str:
    id_, _, text_decoded, _, _, translation, _, ref, _ = row
    text = translation if translation else text_decoded
    if game_id == 'starocean':
        return f"{ref}\r\n{text}\r\n\r\n\r\n"
    elif game_id == 'soe':
        return f"{text}<End>\n"
    elif game_id == 'smrpg':
        # Mirror the import: the dialogues/battleDialogues split comes from the
        # `filename` field, and the per-file index is `file_index` minus the
        # same offset the import added (battle -> 4097, dialogues -> 1).
        is_battle = 'battle' in (filename or '').lower()
        offset = SMRPG_BATTLE_ID_OFFSET if is_battle else 1
        return f"{{{int(file_index) - offset:04d}}}\t{text}\r\n"
    elif game_id == 'ffmq':
        meta = parse_metadata(ref)
        return f"[BLOCK {meta['ID']}: {meta['START']} to {meta['END']}]\r\n{text}\r\n\r\n"
    return f"{ref}\r\n{text}\r\n\r\n"

def _file_index_sort_key(file_index):
    """Order entries by file_index ascending, numeric first then anything else."""
    try:
        return (0, int(file_index))
    except (TypeError, ValueError):
        return (1, str(file_index))

def _safe_destination_path(destination_dump_path, filename):
    """Resolve a stored `filename` inside the destination folder.

    Stored names can be relative sub-paths; anything absolute or escaping the
    destination (`..`) is collapsed to its basename so the export always writes
    inside the folder it was given.
    """
    relative = os.path.normpath(filename.replace('\\', '/'))
    if os.path.isabs(relative) or relative.split(os.sep)[0] == '..':
        relative = os.path.basename(relative)
    return os.path.join(destination_dump_path, relative)

def export_translation(db, destination_dump_path, user_name, blocks, game_id=None) -> None:
  with sqlite3.connect(db) as conn:
    conn.text_factory = str
    cur = conn.cursor()
    if user_name:
      rows = select_translation_by_author(cur, user_name, blocks).fetchall()
    else:
      rows = select_most_recent_translation(cur, blocks).fetchall()
    file_map = {r[0]: (r[1], r[2]) for r in select_text_file_locations(cur).fetchall()}
    if os.path.isdir(destination_dump_path):
      # Folder destination: split the dump into one file per `filename`,
      # ordering the entries within each file by `file_index` (asc).
      groups = {}
      for row in rows:
        filename, file_index = file_map.get(row[0], ('', None))
        groups.setdefault(filename or 'dump.txt', []).append((file_index, row))
      for filename, items in groups.items():
        items.sort(key=lambda item: _file_index_sort_key(item[0]))
        # `filename` may carry the sub-path it was dumped from: recreate it.
        out_path = _safe_destination_path(destination_dump_path, filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w') as f:
          for file_index, row in items:
            f.write(_format_export_row(row, game_id, filename, file_index))
    else:
      # File destination: single dump with every entry (unchanged behaviour).
      with open(destination_dump_path, 'w') as f:
        for row in rows:
          filename, file_index = file_map.get(row[0], ('', None))
          f.write(_format_export_row(row, game_id, filename, file_index))
