# -*- coding: utf-8 -*-

import sys, os, re, io

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
	re.compile(r'^.{7}'),
	re.compile(r' {5,}'),
	re.compile(r'\[.+?\]')
]

def cleanFile(filename, filename1, regexList=[], allowDuplicates=True):
	""" applica a ogni linea del file delle espressioni regolari, rimuove opzionalmente le linee duplicate """
	with io.open(filename, mode='r', encoding="utf-8") as f, io.open(filename1, mode='w', encoding="utf-8") as f1:
		linesSeen = set()
		for line in f.readlines():
			for regex in regexList:
				line = regex.sub('', line)
			if allowDuplicates:
				f1.write(line)
			elif line not in linesSeen:
				f1.write(line)
				linesSeen.add(line)

def extractWordsFromFile(filename):
	""" estrae tutte le parole (sequenze separate da uno spazio) da un file """
	words = []
	with io.open(filename, mode='r', encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			wordsToAdd = line.replace('\n', '').replace('\r', '').replace("'", " ").split(" ")
			wordsToAdd = filter(None, wordsToAdd)
			for word in wordsToAdd:
				if word + ' ' in line:
					wordsToAdd.append(word + ' ')
					wordsToAdd.remove(word)
			words += wordsToAdd
	return words

def extractLinesFromFile(filename):
	""" estrae tutte le linee da un file """
	lines = []
	with io.open(filename, mode='r', encoding="utf-8") as f:
		lines = f.readlines()
	return lines

def wordRegexFilter(words, regexList):
	""" ripulisce le parole da caretteri e byte inutili """
	if words and regexList:
		for regex in regexList:
			words = list(map(lambda x: regex.sub('', x), words))
		words = list(filter(lambda x: x and x != '', words))
	return words if words else []

def syllableCounter(list, min=2, max=3):
	"""  """
	dictionary = {}
	if list:
		for elem in list:
			if len(elem) >= min:
				for i in range(min, max+1):
					for k in range(0, len(elem)):
						syllable = elem[k:k+i]
						if len(syllable) >= i:
							if syllable not in dictionary:
								dictionary[syllable] = 0
							dictionary[syllable] = dictionary[syllable] + 1
	return dictionary

def wordCounter(words, min=2, max=3):
	"""  """
	dictionary = {}
	if words:
		for word in words:
			if len(word) in range(min, max+1):
				if word not in dictionary:
					dictionary[word] = 0
				dictionary[word] = dictionary[word] + 1
	return dictionary

def calculateWeight(dictionary):
	""" crea un dizionario pesato sulla lunghezza delle parole """
	return {k: v * (len(k) - 2) for k, v in dictionary.items()}

def sortDictByValue(dictionary, reverse=True):
	""" reversa il dizionario ordinandolo per il peso """
	return sorted(dictionary.iteritems(), key=lambda(k,v):(v,k), reverse=reverse)

cleanFile(filename, filename1, regexList=SMRPG_REGEX_LIST, allowDuplicates=False)
words = extractWordsFromFile(filename1)
##words = extractLinesFromFile(filename1)
#print("---------")
filteredWords = wordRegexFilter(words, None)
#print("---------")
#print(filteredWords)
dictionary = wordCounter(filteredWords, min=MIN, max=MAX)
##dictionary = syllableCounter(filteredWords, min=MIN, max=MAX)
#print("---------")
#print(dictionary)
weightDictionary = calculateWeight(dictionary)
#print("---------")
#print(weightDictionary)
weightDictionaryByValue = sortDictByValue(weightDictionary)
#print weightDictionaryByValue
#print weightDictionaryByValue[:LIMIT]
with io.open(filename2, mode='w', encoding="utf-8") as out:
	for i, e in enumerate(weightDictionaryByValue[:LIMIT]):
		n = hex(i + offset).rstrip('L')
		b = (n + '').replace('0x', '')
		b = b.zfill(4)
		line = "%s=%s" % (b, e[0])
		out.write(line + '\n')
