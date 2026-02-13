__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import argparse
import re
from collections import Counter
from io import StringIO
from operator import itemgetter

def clean_file(f, f_out, regex_list=None, allow_duplicates=True):
    """Cleans a file using regex and removes duplicates (default)."""
    lines_seen = set()
    for line in f:
        if regex_list:
            for regex, replacement in regex_list:
                line = regex.sub(replacement, line)
        if allow_duplicates:
            f_out.write(line)
        elif line not in lines_seen:
            f_out.write(line)
            lines_seen.add(line)

def clean_string(string, regex_list=None, allow_duplicates=False):
    """Applies regular expressions to a string and optionally removes duplicate lines."""
    if regex_list:
        for regex, replacement in regex_list:
            string = regex.sub(replacement, string)
    if not allow_duplicates:
        string = "\n".join(dict.fromkeys(string.splitlines()))
    return string

def extract_substrings(text, substring_length, start_index=0):
    """Extracts substrings of a given length from a string, starting at a given index."""
    return [text[i:(i+substring_length)] for i in range(start_index, len(text), substring_length)]

def get_substrings_by_length(text, length):
    """Extracts all possible substrings of a given length using a sliding window."""
    if length <= 0 or length > len(text):
        return []
    return [text[i:i+length] for i in range(len(text) - length + 1)]

def get_occurrences_by_length(f, length):
    """Generates a Counter of substring occurrences of a specific length."""
    dictionary = Counter()
    for line in f:
        clean_line = line.strip('\r\n')
        if clean_line:
            substrings = get_substrings_by_length(clean_line, length)
            dictionary.update(substrings)
    return dictionary

def get_occurrences(f, min_length, max_length):
    """Generates a dictionary of string occurrences within a length range."""
    dictionary = Counter()
    for length in range(min_length, max_length + 1):
        f.seek(0)
        occurrences = Counter(get_occurrences_by_length(f, length))
        dictionary.update(occurrences)
    return dictionary

def calculate_weight(dictionary, num_bytes):
    """Calculates weights, only keeping strings that provide a positive compression gain."""
    return {
        k: v * (len(k) - num_bytes)
        for k, v in dictionary.items()
        if len(k) > num_bytes
    }

def sort_dict_by_value(dictionary, reverse=True):
    """Sorts a dictionary by value (and then key)."""
    return sorted(dictionary.items(), key=itemgetter(1, 0), reverse=reverse)

def calculate_weighted_sum(dictionary, num_bytes):
    """Calculates the weighted sum of values in a dictionary based on key length."""
    return sum(value * (len(key) - num_bytes) for key, value in dictionary.items())

def string_to_file(filename, s):
    with open(filename, mode='w', encoding="utf-8") as f:
        f.write(str(s))

def get_regex_list(game):
    if game == 'bof':
        return None
    elif game == 'gargoyle':
        return [
            (re.compile(r'<WAIT>\n'), '\n'),
            (re.compile(r'{..}'), ''),
            (re.compile(r'\[.+?\]'), '\n')
        ]
    elif game == 'smrpg':
        return [
            (re.compile(r'^.{7}'), ''),
            (re.compile(r' {5,}'), ''),
            (re.compile(r'[.]{3,}'), '\n'),
            (re.compile(r'\[.+?\]'), '\n')
        ]
    elif game == 'som':
        return [
            (re.compile(r'\[BOY\]'), 'BOY456'),
            (re.compile(r'\[GIRL\]'), 'GIRL56'),
            (re.compile(r'\[SPRITE\]'), 'SPRITE'),
            (re.compile(r'\[.*?\]'), '')
        ]
    elif game == 'starocean':
        return [
            (re.compile(r'^<TEXT .*?>\n'), ''),
            (re.compile(r'^</TEXT>\n'), ''),
            (re.compile(r'<\$..>'), '')
        ]
    elif game == 'ys4':
        return None
    else:
        return None

def process_dictionary(args):
    min_length = args.min
    max_length = args.max
    limit = args.limit
    num_bytes = args.bytes
    source_path = args.source_file
    clean_path = args.clean_file
    game = args.game
    debug = args.debug
    #
    regex_list = get_regex_list(game)
    with open(source_path, mode='r', encoding="utf-8") as f_in, open(clean_path, mode='w', encoding="utf-8") as f_out:
        clean_file(f_in, f_out, regex_list=regex_list, allow_duplicates=False)
    dictionary = {}
    with open(clean_path, mode='r', encoding="utf-8") as f:
        buff = StringIO(f.read())
        for i in range(0, limit):
            occurrences = get_occurrences(buff, min_length, max_length)
            occurrences_with_weight = calculate_weight(occurrences, num_bytes)
            sorted_dictionary = sort_dict_by_value(occurrences_with_weight)
            best_string, weight = sorted_dictionary[0]
            dictionary[best_string] = weight
            new_content = clean_string(
                buff.getvalue(),
                regex_list=[(re.compile(re.escape(best_string)), '\n')],
                allow_duplicates=True
            )
            buff = StringIO(new_content)
            if debug:
                string_to_file(f'{clean_path}.{i}', buff.getvalue())
    return dictionary

def handle_print(args):
    num_bytes = args.bytes
    dictionary = process_dictionary(args)
    print(dictionary)
    print(calculate_weighted_sum(dictionary, num_bytes))

def handle_table(args):
    num_bytes = args.bytes
    dest_file = args.dest_file
    offset = args.offset
    dictionary = process_dictionary(args)
    with open(dest_file, mode='w', encoding="utf-8") as out:
        for i, (key, _) in enumerate(dictionary.items()):
            line = key
            if offset is not None:
                prefix = hex(i + offset).replace('0x', '').zfill(num_bytes * 2)
                line = f'{prefix}={key}'
            out.write(f'{line}\n')

parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument('-m', '--min', type=int, default=3, help='Minimum string length to consider for the dictionary (default: 3)')
parent_parser.add_argument('-M', '--max', type=int, default=8, help='Maximum string length to consider for the dictionary (default: 8)')
parent_parser.add_argument('-l', '--limit', type=int, default=5, help='Maximum number of dictionary entries to extract (default: 5)')
parent_parser.add_argument('-b', '--bytes', type=int, default=2, help='Size of the dictionary key (pointer) in bytes (default: 2)')
parent_parser.add_argument('-s', '--source', dest='source_file', required=True, help='Path to the original source text file')
parent_parser.add_argument('-c', '--clean', dest='clean_file', required=True, help='Path to save the pre-processed "clean" text file')
parent_parser.add_argument('--game', choices=['bof', 'gargoyle', 'smrpg', 'som', 'starocean', 'ys4'], help='Apply game-specific regex cleaning rules')
parent_parser.add_argument('--debug', action='store_true', help='Enable debug mode: saves intermediate buffer states to disk')
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='cmd', required=True, help='Available commands')
p_print = subparsers.add_parser('print', parents=[parent_parser], help='Extract dictionary and display compression statistics')
p_print.set_defaults(func=handle_print)
p_table = subparsers.add_parser('table', parents=[parent_parser], help='Extract dictionary and export to a .tbl mapping file')
p_table.add_argument('-d', '--dest', dest='dest_file', required=True, help='Path to the destination .tbl file')
p_table.add_argument('-o', '--offset', type=int, help='Starting hexadecimal or decimal offset for table mapping (e.g., 0x80 or 128)')
p_table.set_defaults(func=handle_table)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.func:
    args.func(args)
  else:
    parser.print_help()
