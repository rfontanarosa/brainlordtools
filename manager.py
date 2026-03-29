__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os
import sys

from brainlordtools.utils.actions import copy_file, crc_check, diff_dump, expand_file, export_translation, import_dump, import_translation
from brainlordtools.utils.translators import amazon_translate_processor, deepl_translate_processor

def handle_copy_file(args):
    source_file = args.source_file
    dest_file = args.dest_file
    copy_file(source_file, dest_file)

def handle_crc_check(args):
    source_file = args.source_file
    game_id = args.game_id
    crc_check(source_file, game_id)

def handle_diff_dump(args):
    source1_dump_path = args.source1
    source2_dump_path = args.source2
    destination_dump_path = args.destination
    game_id = args.game_id
    diff_dump(source1_dump_path, source2_dump_path, destination_dump_path, game_id)

def handle_expand_file(args):
    dest_file = args.dest_file
    game_id = args.game_id
    expand_file(dest_file, game_id)

def handle_import_dump(args):
    db = args.database_file
    source_dump_path = args.source
    game_id = args.game_id
    import_dump(db, source_dump_path, game_id)

def handle_import_translation(args):
    db = args.database_file
    source_dump_path = args.source
    user_name = args.user_name
    original_dump_path = args.original_dump
    game_id = args.game_id
    import_translation(db, source_dump_path, user_name, original_dump_path, game_id)

def handle_export_translation(args):
    db = args.database_file
    destination_dump_path = args.destination
    user_name = args.user_name
    blocks = args.blocks
    export_translation(db, destination_dump_path, user_name, blocks)

def handle_amazon_translate_processor(args) -> None:
    source_dump_path = args.source
    destination_dump_path = args.destination
    game_id = args.game_id
    amazon_translate_processor(source_dump_path, destination_dump_path, game_id)

def handle_deepl_translate_processor(args) -> None:
    source_dump_path = args.source
    destination_dump_path = args.destination
    auth_key = os.getenv("DEEPL_AUTH_KEY")
    if not auth_key:
        sys.exit("Error: DEEPL_AUTH_KEY environment variable not set.")
    deepl_translate_processor(source_dump_path, destination_dump_path, auth_key)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser('copy_file', help='File COPY')
    sub.add_argument('-s', '--source', dest='source_file', required=True, help='Path to the original file to be copied')
    sub.add_argument('-d', '--dest', dest='dest_file', required=True, help='Path to the destination file where the copy will be saved')
    sub.set_defaults(func=handle_copy_file)

    sub = subparsers.add_parser('crc_check', help='Check file CRC')
    sub.add_argument('-s', '--source', dest='source_file', required=True, help='Path to the file to be checked')
    sub.add_argument('-g', '--game', dest='game_id', required=True, help='Game ID (e.g., som, ff6)')
    sub.set_defaults(func=handle_crc_check)

    sub = subparsers.add_parser('diff_dump', help='Generate a diff between two dump files')
    sub.add_argument('-s1', '--source1', action='store', dest='source1', required=True, help='Path to the 1st source .txt dump file')
    sub.add_argument('-s2', '--source2', action='store', dest='source2', required=True, help='Path to the 2nd source .txt dump file')
    sub.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Path to the generated .txt dump')
    sub.add_argument('-g', '--game', action='store', dest='game_id', required=False, default='default', help='Optional: Game ID (e.g., som, ff6) to use for custom parsing logic')
    sub.set_defaults(func=handle_diff_dump)

    sub = subparsers.add_parser('expand')
    sub.add_argument('-d', '--dest', dest='dest_file', required=True, help="Path to the destination file to be expanded")
    sub.add_argument('-g', '--game', dest='game_id', required=True, help="Game ID (e.g., som, ff6)")
    sub.set_defaults(func=handle_expand_file)

    sub = subparsers.add_parser('import_dump', help='Import source from a dump file')
    sub.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='Path to the SQLite database')
    sub.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the source .txt dump file')
    sub.add_argument('-g', '--game', action='store', dest='game_id', required=False, default='default', help='Optional: Game ID (e.g., som, ff6) to use for custom parsing logic')
    sub.set_defaults(func=handle_import_dump)

    sub = subparsers.add_parser('import_translation', help='Import translations from a dump file')
    sub.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='Path to the SQLite database')
    sub.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the translated .txt dump file')
    sub.add_argument('-u', '--user', action='store', dest='user_name', required=True, help='The author of the translation')
    sub.add_argument('-od', '--original_dump', action='store', dest='original_dump', required=False, help='Path to the source .txt original dump file')
    sub.add_argument('-g', '--game', action='store', dest='game_id', required=False, default='default',help='Optional: Game ID (e.g., som, ff6) to use for custom parsing logic')
    sub.set_defaults(func=handle_import_translation)

    sub = subparsers.add_parser('export_translation', help='Export translations to a dump file')
    sub.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='Path to the SQLite database')
    sub.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Output path for the generated .txt dump')
    sub.add_argument('-u', '--user', action='store', dest='user_name', required=False, help='The author whose translations you want to export')
    sub.add_argument('-b', '--blocks', action='store', dest='blocks', required=False, nargs='+', help='Optional: Filter by specific block IDs')
    sub.set_defaults(func=handle_export_translation)

    sub = subparsers.add_parser('amazon', help='Translate a dump using Amazon service')
    sub.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the source .txt dump file')
    sub.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Output path for the generated .txt dump')
    sub.add_argument('-g', '--game', action='store', dest='game_id', required=False, help='Optional: Game ID (e.g., som, ff6) to use for custom parsing logic')
    sub.set_defaults(func=handle_amazon_translate_processor)

    sub = subparsers.add_parser('deepl', help='Translate a dump using Deepl service')
    sub.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the source .txt dump file')
    sub.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Output path for the generated .txt dump')
    sub.set_defaults(func=handle_deepl_translate_processor)

    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

