import re, io
from collections import defaultdict, Counter
from io import StringIO

import argparse
parent_parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest='cmd')
parent_parser.add_argument('-m', '--min', action='store', dest='min', type=int, default=3, help='')
parent_parser.add_argument('-M', '--max', action='store', dest='max', type=int, default=8, help='')
parent_parser.add_argument('-l', '--limit', action='store', dest='limit', type=int, default=5, help='')
parent_parser.add_argument('-b', '--bytes', action='store', dest='bytes', type=int, default=2, help='')
parent_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
parent_parser.add_argument('-c', '--clean', action='store', dest='clean_file', required=True, help='Clean filename')
parent_parser.add_argument('--game', choices=['bof', 'gargoyle', 'smrpg', 'ys4'], help='Game specific cleaning rules')
parent_parser.add_argument('--debug', action='store_true', help='Enable DEBUG')
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
    """ applica a ogni linea del file delle espressioni regolari, rimuove opzionalmente le linee duplicate """
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

def clean_string(string, regex_list=None, allow_duplicates=True):
    """ applica a ogni linea del file delle espressioni regolari, rimuove opzionalmente le linee duplicate """
    s = StringIO(string)
    s1 = StringIO()
    lines_seen = set()
    for line in s.readlines():
        if regex_list:
            for regex in regex_list:
                line = regex[0].sub(regex[1], line)
        if allow_duplicates:
            s1.write(line)
        elif line not in lines_seen:
            s1.write(line)
            lines_seen.add(line)
    return s1.getvalue()

def string_to_file(filename, s):
    with io.open(filename, mode='w', encoding="utf-8") as f:
        f.write(s)

def extract_chunks(text, chunk_size, start_index=0):
    """ estrae le occorrenze di lunghezza n da una stringa """
    return [text[i:(i+chunk_size)] for i in range(start_index, len(text), chunk_size)]

def get_substrings_by_length(text, length):
    """ estrae tutte le possibili occorrenze di lunghezza n da una stringa """
    chunks = []
    if length > 0:
        for i in range (0, length):
            chunks += extract_chunks(text, length, i)
    return list(filter(lambda x: len(x) == length, chunks))

def get_occurrences_by_length(f, length):
    """ genera un dizionario con le occorrenze di lunghezza n """
    dictionary = defaultdict(int)
    for line in f.readlines():
        if line:
            line = line.replace('\n', '').replace('\r', '')
            substrings = get_substrings_by_length(line, length)
            for string in substrings:
                dictionary[string] += 1
    return dictionary

def get_occurrences(f, min_length, max_length):
    """ genera un dizionario con le occorrenze di un range di lunghezza """
    dictionary = Counter()
    for length in range(min_length, max_length + 1):
        buff = StringIO(f.getvalue())
        occurrences = Counter(get_occurrences_by_length(buff, length))
        dictionary.update(occurrences)
    return dictionary

def calculate_weight(dictionary):
    """ crea un dizionario pesato sulla lunghezza delle parole """
    return {k: v * (len(k) - 2) for k, v in dictionary.items()}

def sort_dict_by_value(dictionary, reverse=True):
    """ reversa il dizionario e lo ordina per valore """
    return sorted(list(dictionary.items()), key=lambda x: (x[1], x[0]), reverse=reverse)

def export_table(filename, dictionary, offset):
    with io.open(filename, mode='w', encoding="utf-8") as out:
        for i, v in enumerate(dictionary):
            line = v
            if offset is not None:
                n = hex(i + offset).rstrip('L')
                b = (n + '').replace('0x', '')
                b = b.zfill(BYTES * 2)
                line = f'{b}={v}'
            out.write(f'{line}\n')

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
elif cmd == 'table':
    print(dictionary)
    export_table(filename2, dictionary, offset)
