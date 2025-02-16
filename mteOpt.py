import io, re
from collections import Counter
from io import StringIO

import argparse
parent_parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest='cmd')
parent_parser.add_argument('-m', '--min', action='store', dest='min', type=int, default=3, help='Minimum string length')
parent_parser.add_argument('-M', '--max', action='store', dest='max', type=int, default=8, help='Maximum string length')
parent_parser.add_argument('-l', '--limit', action='store', dest='limit', type=int, default=5, help='Dictionary number of entries')
parent_parser.add_argument('-b', '--bytes', action='store', dest='bytes', type=int, default=2, help='Dictionary key lenght')
parent_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
parent_parser.add_argument('-c', '--clean', action='store', dest='clean_file', required=True, help='Clean filename')
parent_parser.add_argument('--game', choices=['bof', 'gargoyle', 'smrpg', 'starocean', 'ys4'], help='Game specific cleaning rules')
parent_parser.add_argument('--debug', action='store_true', help='Enable debug output')
parser0 = subparsers.add_parser('print' , parents=[parent_parser], add_help=False)
parser1 = subparsers.add_parser('table', parents=[parent_parser], add_help=False)
parser1.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
parser1.add_argument('-o', '--offset', action='store', dest='offset', type=int, help='Starting offset')
args = parser.parse_args()
dict_args = vars(args)

cmd = dict_args.get('cmd')
MIN = dict_args.get('min')
MAX = dict_args.get('max')
LIMIT = dict_args.get('limit')
BYTES = dict_args.get('bytes')
filename = dict_args.get('source_file')
filename1 = dict_args.get('clean_file')
game = dict_args.get('game')
debug = dict_args.get('debug')
filename2 = dict_args.get('dest_file')
offset = dict_args.get('offset')

def clean_file(f, f1, regex_list=None, allow_duplicates=True):
    """Cleans a file using regex and removes duplicates (default)."""
    lines_seen = set()
    for line in f.readlines():
        if regex_list:
            for regex in regex_list:
                line = regex[0].sub(regex[1], line)
        if allow_duplicates:
            f1.write(line)
        elif line not in lines_seen:
            f1.write(line)
            lines_seen.add(line)

def clean_string(string, regex_list=None, allow_duplicates=False):
    """Applies regular expressions to a string and optionally removes duplicate lines."""
    if regex_list:
        for regex, replacement in regex_list:
            string = regex.sub(replacement, string)
    if not allow_duplicates:
        lines = string.splitlines()
        unique_lines = []
        seen = set()
        for line in lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)
        string = "\n".join(unique_lines)
    return string

def extract_substrings(text, substring_length, start_index=0):
    """Extracts substrings of a given length from a string, starting at a given index."""
    return [text[i:(i+substring_length)] for i in range(start_index, len(text), substring_length)]

def get_substrings_by_length(text, length):
    """Extracts all possible substrings of a given length from a string."""
    substrings = []
    if length > 0:
        for i in range (0, length):
            substrings += extract_substrings(text, length, i)
    return list(filter(lambda x: len(x) == length, substrings))

def get_occurrences_by_length(f, length):
    """Generates a dictionary of substring occurrences of a specific length from a file."""
    dictionary = Counter()
    for line in f.readlines():
        if line:
            line = line.replace('\n', '').replace('\r', '')
            substrings = get_substrings_by_length(line, length)
            for string in substrings:
                dictionary[string] += 1
    return dictionary

def get_occurrences(f, min_length, max_length):
    """Generates a dictionary of string occurrences within a length range."""
    dictionary = Counter()
    for length in range(min_length, max_length + 1):
        buff = StringIO(f.getvalue())
        occurrences = Counter(get_occurrences_by_length(buff, length))
        dictionary.update(occurrences)
    return dictionary

def calculate_weight(dictionary):
    """Calculates weights based on string length."""
    return {k: v * (len(k) - BYTES) for k, v in dictionary.items()}

def sort_dict_by_value(dictionary, reverse=True):
    """Sorts a dictionary by value (and then key)."""
    return sorted(dictionary.items(), key=lambda item: (item[1], item[0]), reverse=reverse)

def export_table(filename, dictionary, offset):
    """Exports the dictionary to a table with optional offset."""
    with io.open(filename, mode='w', encoding="utf-8") as out:
        for i, v in enumerate(dictionary):
            line = v
            if offset is not None:
                n = hex(i + offset).rstrip('L')
                b = (n + '').replace('0x', '')
                b = b.zfill(BYTES * 2)
                line = f'{b}={v}'
            out.write(f'{line}\n')

def calculate_weighted_sum(dictionary):
    """Calculates the weighted sum of values in a dictionary based on key length."""
    return sum(value * (len(key) - BYTES) for key, value in dictionary.items())

def string_to_file(filename, s):
    with io.open(filename, mode='w', encoding="utf-8") as f:
        f.write(s)

regex_list = None

if game == 'bof':
    pass
elif game == 'gargoyle':
    regex_list = [
        (re.compile(r'<WAIT>\n'), '\n'),
        (re.compile(r'{..}'), ''),
        (re.compile(r'\[.+?\]'), '\n')
    ]
elif game == 'smrpg':
    regex_list = [
        (re.compile(r'^.{7}'), ''),
        (re.compile(r' {5,}'), ''),
        (re.compile(r'[.]{3,}'), '\n'),
        (re.compile(r'\[.+?\]'), '\n')
    ]
elif game == 'starocean':
    regex_list = [
        (re.compile(r'^<TEXT .*?>\n'), ''),
        (re.compile(r'^</TEXT>\n'), ''),
        (re.compile(r'<\$..>'), '')
    ]
elif game == 'ys4':
    pass

with io.open(filename, mode='r', encoding="utf-8") as f, io.open(filename1, mode='w', encoding="utf-8") as f1:
    clean_file(f, f1, regex_list=regex_list, allow_duplicates=False)

dictionary = {}
with io.open(filename1, mode='r', encoding="utf-8") as f:
    buff = StringIO(f.read())
    for i in range(0, LIMIT):
        occurrences = get_occurrences(buff, MIN, MAX)
        occurrences_with_weight = calculate_weight(occurrences)
        sorted_dictionary = sort_dict_by_value(occurrences_with_weight)
        k, v = sorted_dictionary[0]
        dictionary[k] = v
        buff = StringIO(clean_string(buff.getvalue(), regex_list=[(re.compile(re.escape(k)), '\n')], allow_duplicates=True))
        if debug:
            string_to_file(f'{filename1}.{i}', buff.getvalue())

if cmd == 'print':
    print(dictionary)
    print(calculate_weighted_sum(dictionary))
elif cmd == 'table':
    export_table(filename2, dictionary, offset)
