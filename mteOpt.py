import sys, os
from collections import OrderedDict

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--min', action='store', dest='min', type=int, required=True, help='')
parser.add_argument('-M', '--max',  action='store', dest='max', type=int, required=True, help='')
parser.add_argument('-l', '--limit',  action='store', dest='limit', type=int, required=True, help='')
parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
parser.add_argument('-d', '--dest',  action='store', dest='dest_file', required=True, help='Destination filename')
parser.add_argument('-o', '--offset',  action='store', dest='offset', type=int, required=True, help='Starting offset')
args = parser.parse_args()

MIN = args.min
MAX = args.max
LIMIT = args.limit
filename = args.source_file
filename2 = args.dest_file
offset = args.offset

def extractWordsFromFile(filename):
	""" estrae tutte le parole (sequenze separate da uno spazio) da un file """
	words = []
	with open(filename, 'rb') as f:
		lines = f.readlines()
		for line in lines:
			wordsToAdd = line.replace('\n', '').replace('\r', '').replace("'", " ").split(" ")
			wordsToAdd = filter(None, wordsToAdd)
			for word in wordsToAdd:
				if word + ' ' in line:
					pass
					wordsToAdd.append(word + ' ')
					wordsToAdd.remove(word)
			words += wordsToAdd
	return words

def extractLinesFromFile(filename):
	""" estrae tutte le linee da un file """
	lines = []
	with open(filename, 'rb') as f:
		lines = f.readlines()
	return lines

def characterFilter(list):
	""" ripulisce le parole da caretteri e byte inutili """
	filteredList = []
	if list:
		for index, elem in enumerate(list):
			filtered = list[index].replace("\n", "").replace("\r", "")
			filtered = filtered.replace(",", "").replace(";", "").replace(".", "").replace("!", "").replace("?", "")
			filtered = filtered.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
			filtered = filtered.replace("+", "").replace(":", "")
			if filtered and filtered != '':
				filteredList.append(filtered)
	return filteredList

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
	""" """
	weightDictionary = {}
	for key in dictionary:
		weightDictionary[key] = dictionary[key] * (len(key) - 2)
	return weightDictionary

def sortDictByValue(dictionary, reverse=True):
	""" """
	return sorted(dictionary.iteritems(), key=lambda(k,v):(v,k), reverse=reverse)

words = extractWordsFromFile(filename)
##words = extractLinesFromFile(filename)
#print "---------"
#print words
filteredList = characterFilter(words)
#print "---------"
#print filteredList
dictionary = wordCounter(filteredList, min=MIN, max=MAX)
##dictionary = syllableCounter(filteredList, min=MIN, max=MAX)
#print "---------"
#print dictionary
weightDictionary = calculateWeight(dictionary)
#print "---------"
weightDictionaryByValue = sortDictByValue(weightDictionary)
#print weightDictionaryByValue
#print weightDictionaryByValue[:LIMIT]
with open(filename2, 'w') as out:
	for i, e in enumerate(weightDictionaryByValue[:LIMIT]):
		n = hex(i + offset).rstrip('L')
		b = (n + '').replace('0x', '')
		b = b.zfill(4)
		line = "%s=%s" % (b, e[0])
		out.write(line + '\n')