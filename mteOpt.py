# -*- coding: utf-8 -*-

import sys, os, re, io
from shutil import copyfile
from collections import defaultdict, Counter, OrderedDict

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--min', action='store', dest='min', type=int, required=True, help='')
parser.add_argument('-M', '--max',  action='store', dest='max', type=int, required=True, help='')
parser.add_argument('-l', '--limit',  action='store', dest='limit', type=int, required=True, help='')
parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
parser.add_argument('-c', '--clean', action='store', dest='clean_file', required=True, help='Clean filename')
parser.add_argument('-d', '--dest',  action='store', dest='dest_file', required=True, help='Destination filename')
parser.add_argument('-o', '--offset',  action='store', dest='offset', type=int, required=True, help='Starting offset')
args = parser.parse_args()

MIN = args.min
MAX = args.max
LIMIT = args.limit
filename = args.source_file
filename1 = args.clean_file
filename2 = args.dest_file
offset = args.offset

SMRPG_REGEX_LIST = [
	(re.compile(r'^.{7}'), ''),
	(re.compile(r' {5,}'), ''),
	(re.compile(r'[.]{3,}'), '\n'),
	(re.compile(r'\[.+?\]'), '\n')
]

def clean_file(filename, filename1, regexList=[], allowDuplicates=True):
	""" applica a ogni linea del file delle espressioni regolari, rimuove opzionalmente le linee duplicate """
	with io.open(filename, mode='r', encoding="utf-8") as f, io.open(filename1, mode='w', encoding="utf-8") as f1:
		linesSeen = set()
		for line in f.readlines():
			for regex in regexList:
				line = regex[0].sub(regex[1], line)
			if allowDuplicates:
				f1.write(line)
			elif line not in linesSeen:
				f1.write(line)
				linesSeen.add(line)

def extract_chunks(text, chunkSize, startPoint=0):
	""" estrae le occorrenze di lunghezza n da una stringa """
	return [text[i:(i+chunkSize)] for i in range(startPoint, len(text), chunkSize)]

def get_substrings_by_length(text, length):
	""" estrae tutte le possibili occorrenze di lunghezza n da una stringa """
	chunks = []
	if length > 0:
		for i in range (0, length):
			chunks += extract_chunks(text, length, i)
	return list(filter(lambda x: len(x) == length, chunks))

def get_occurrences_by_length(filename, length):
	""" genera un dizionario con le occorrenze di lunghezza n """
	dictionary = defaultdict(int)
	with io.open(filename, mode='r', encoding="utf-8") as f:
		for line in f.readlines():
			if line:
				line = line.replace('\n', '').replace('\r', '')
				substrings = get_substrings_by_length(line, length)
				for string in substrings: dictionary[string] += 1
	return dictionary

def get_occurrences(filename, min_length, max_length):
	""" genera un dizionario con le occorrenze di un range di lunghezza """
	dictionary = Counter()
	for length in range(min_length, max_length + 1):
		occurrences = Counter(get_occurrences_by_length(filename, length))
		dictionary.update(occurrences)
	return dictionary

def calculate_weight(dictionary):
	""" crea un dizionario pesato sulla lunghezza delle parole """
	return {k: v * (len(k) - 2) for k, v in dictionary.items()}

def sort_dict_by_value(dictionary, reverse=True):
	""" reversa il dizionario e lo ordina per valore """
	return sorted(dictionary.iteritems(), key=lambda(k,v):(v,k), reverse=reverse)

def export_table(filename, dictionary, offset):
	with io.open(filename, mode='w', encoding="utf-8") as out:
		for i, v in enumerate(dictionary):
			n = hex(i + offset).rstrip('L')
			b = (n + '').replace('0x', '')
			b = b.zfill(4)
			line = "%s=%s" % (b, v)
			out.write(line + '\n')

clean_file(filename, filename1, regexList=SMRPG_REGEX_LIST, allowDuplicates=False)
dictionary = OrderedDict()
curr_filename = filename1
for i in range(0, LIMIT):
	next_filename = filename1 + '.' + str(i)
	occurrences = get_occurrences(curr_filename, MIN, MAX)
	occurrences_with_weight = calculate_weight(occurrences)
	sorted_dicionary = sort_dict_by_value(occurrences_with_weight)
	k, v = sorted_dicionary[0]
	dictionary[k] = v
	clean_file(curr_filename, next_filename, regexList=[(re.compile(re.escape(k)), '\n')], allowDuplicates=True)
	curr_filename = next_filename
export_table(filename2, dictionary, offset)
