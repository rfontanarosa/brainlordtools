"""
brainlord_repointer
last version: 2009-03-05 (0.45)
changes: see _readme.txt
author: roberto fontanarosa (robertofontanarosa@hotmail.com)
"""

import sys

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit('err')
	
import os
from os import SEEK_SET, SEEK_CUR, SEEK_END
import mmap

import pdb

# TODO check dell'header
# TODO l'header e sempre di 100 bytes?
# HEADER = 0xc8 

# TODO come riconoscere se una rom e lo o hi?
# SNES_LO-ROM_OFFSET = C00000

# TODO checksum delle rom (sia senza che con l'header)
# BRAIN LORD (U) [!] SENZA HEADER - CHECKSUM CRC32: 8275d8

# TODO trovare un modo per verificare se e presente o meno l'header
# TODO aggiungere agli indirizzi i byte dell'header SE questo e presente
TEXT_BLOCK_START = 0x170000
TEXT_BLOCK_END = 0x17fac9
TEXT_BLOCK_LIMIT = 0x17ffff

TEXT_BLOCK_SIZE = TEXT_BLOCK_END - TEXT_BLOCK_START
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

TEXT_POINTER1_BLOCK_START = 0xf9e
TEXT_POINTER1_BLOCK_END = 0xfef

TEXT_POINTER2_BLOCK_START = 0x50010
TEXT_POINTER2_BLOCK_END = 0x55567

## there are 20 (?) pointers in this block and every pointer starts with 0x01
#FAERIES_POINTER_START_BYTE = 0x01
FAERIES_POINTER_BLOCK_START = 0x18ea0
FAERIES_POINTER_BLOCK_END = 0x18f9b

def dec2hex(n):
	"""return the hexadecimal string representation of integer n"""
	return "%x" % n
	
def hex2dec(s):
	"""return the integer value of a hexadecimal string s"""
	return int(s, 16) 

def int2byte(n):
	"""return a string value of a int value"""
	return chr(n)
	
def readed_to_int(readed):
	"""  """
	integer = 0
	for x in readed:
		integer = (integer << 8) | ord(x)
	return integer

def to_little_endian(p):
	"""  """
	pointer = p[4:6] + p[2:4] + 'd7'
	return pointer
	
def to_big_endian(p):
	"""  """
	pointer = 'd7' + p[2:4] + p[0:2]
	return pointer

def pointer_finder(f, pointer_to_find, start=SEEK_SET, previous_seek=None, in_range=True):
	"""  """
	
	addresses_found = []
	
	f.seek(start)
	
	while True:
		# try to find the pointer inside the rom
		# TODO f.find should not use the HexToByte function to convert a pointer
		address = f.find(HexToByte(pointer_to_find), f.tell())
		if (address==-1):
			break
		else:
			# check if in_range option is enabled
			if in_range:
				# check it the address is in the range of is_valid_address
				if is_valid_address(address):
					addresses_found.append(address)
			if not in_range:
				addresses_found.append(address)
		# move the file handler to the next byte
		f.seek(address + 1)
		
	if previous_seek:
		f.seek(previous_seek)

	return addresses_found

	
	
def get_pointers(f, start=SEEK_SET, previous_seek=None):
	"""  """
	pointers = []
	f.seek(start)
	while True:
		byte = f.read(1)
		if not byte:
			break
		if int(0xf7) == readed_to_int(byte):
			byte = f.read(1)
			if int(0xf7) == readed_to_int(byte): # is correct?
				f.seek(f.tell())
				pointer = dec2hex(f.tell())
				pointers.append(to_little_endian(pointer))
			else:
				f.seek(f.tell()-1)
				pointer = dec2hex(f.tell())
				pointers.append(to_little_endian(pointer))
	
	if previous_seek:
		f.seek(previous_seek)		
				
	return pointers

	
def get_pointers_table(f, start=SEEK_SET, previous_seek=None):
	"""  """
	f.seek(start)
	
	pointers_table = {} # struttura che ha per chiave il puntatore e per valore le sue posizioni
	pointers = get_pointers(f, start=start, previous_seek=None)
	for pointer in pointers:
		pointers_table[pointer] = pointer_finder(f, pointer, previous_seek=start)

	if previous_seek:
		f.seek(previous_seek)

	return pointers_table


def dump(f, start=SEEK_SET, end=None, previous_seek=None):
	""" dump in a string a portion of the file """
	dump = "" # string that contains the bytes from and to a specificated offsets 
	f.seek(start)
	while True:
		byte = f.read(1)
		if not byte:
			break
		if end!=None and f.tell()==end:
			break
		dump += byte
	if dump:
		print "totale byte dumpati: %s\n" % len(dump)
		
	if previous_seek:
		f.seek(previous_seek)
		
	return dump


def dump_pointers_table(pointers_table, filename='dump_pointers_table.txt'):
	""" this function print and format in a txt file the content of a dict of lists object """
	f = open(filename, 'w')
	for pointer in pointers_table:
		f.write(pointer + '\t')
		for address in pointers_table[pointer]:
			f.write(address + '\t')
		f.write('\n')
	f.close()


# TODO? rinominare?
# TODO? non conviene usare range()?
def is_valid_address(address):
	"""  """
	return (TEXT_POINTER1_BLOCK_END >= address >= TEXT_POINTER1_BLOCK_START) \
			or (TEXT_POINTER2_BLOCK_END >= address >= TEXT_POINTER2_BLOCK_START) \
			or (FAERIES_POINTER_BLOCK_END >= address >= FAERIES_POINTER_BLOCK_START) \
			or (TEXT_BLOCK_END >= address >= TEXT_BLOCK_START)
"""
cercati e trovati a mano
a99200
a99301
"""
def is_shop_pointer(address):
	"""  """
	return (0x25000 >= address >= 0x23000)
			
def is_in_text_block(address):
	"""  """
	return (TEXT_BLOCK_END >= address >= TEXT_BLOCK_START)
	
	
# TODO creare una funzione per che ritorni le mmap delle rom (per evitare di replicare il codice e i controlli)
# TODO checking di validita dei file via checksum

# apertura della rom ORIGINALE in LETTURA e senza limiti di buffer
filepath = sys.argv[1]
file = open(filepath, "rb+")
size = os.path.getsize(filepath)
# mappatura del file ORIGINALE in memoria
f = mmap.mmap(file.fileno(), size)
file.close()

# apertura della rom MODIFICATA in SCRITTURA e senza limiti di buffer
filepath2 = sys.argv[2]
file2 = open(filepath2, "ab+")
size2 = os.path.getsize(filepath2)
# mappatura del file MODIFICATO in memoria
f2 = mmap.mmap(file2.fileno(), size2)
file2.close()

# trova tutti i puntatori e le relative posizioni all'inetrno della rom
# chaivi trovate con get_pointers, valori trovati con pointer_finder
pointers_table = get_pointers_table(f, TEXT_BLOCK_START) # { pointer : [address, ...] }
# trova tutti i puntatori (f7 singoli) nella rom ORIGINALE e in quella MODIFICATA
o_pointers = get_pointers(f, start=TEXT_BLOCK_START, previous_seek=f.tell())
m_pointers = get_pointers(f2, start=TEXT_BLOCK_START, previous_seek=f2.tell())


"""
- controlla se le liste contenenti i puntatori della rom originale e quelli della rom modificata hanno lo stesso numero di puntatori
- itera la lista dei puntatori della rom originale
- controlla se il puntatore e' presente nella lista dei puntatori
- estrae il corrispondente puntatore (poiche sono in ordine) dalla lista dei puntatori della rom modificata
- controlla se effettivamente nella tabella dei puntatori e' presente il puntatore originale come chiave
se per il puntatore non e' stato trovato nessun indirizzo:
	pass
se per il puntatore e' stato trovato almeno un indirizzo:
	itera gli indirizzi trovati ed effettua un controllo
		se l'indirizzo e' nel banco di testo:
			ricerca nelal rom modificata il puntatore originale per determinarne la nuova posizione e scrive su quell'indirizzo il puntatore modificato
		se l'indirizzo non e' nel banco di testo:
			scrive su quell'indirizzo il puntatore modificato
pass
"""

# controlla se nella rom originale e nella rom modificata ci sono los tesso numero di puntatori
if len(o_pointers)==len(m_pointers):

	## start - counters initialization
	pointers_modified = 0
	pointers_not_found_counter = 0
	## end - counters initialization
	
	shop_pointers = {}

	for o_pointer in o_pointers:
	
		if pointers_table.has_key(o_pointer):
	
			m_pointer = m_pointers.pop(0)
		
			## start - shop repointer 1
			if pointers_table[o_pointer]==[]:	# if any address was found for a pointer...
				pointers_not_found_counter += 1
				adresses = pointer_finder(f, 'a9' + o_pointer[0:4], in_range=False)
				if adresses:
					pointers_not_found_counter -= 1
				#print 'a9' + o_pointer[0:4] + ' - ' + str(h2)
				shop_pointers['a9' + m_pointer[0:4]] = adresses
			## end shop repointer 1
		
			## start - text repointer process
			if pointers_table[o_pointer]!=[]:

				"""
				f0 = open('doc.txt', 'a')		
				aaa = o_pointer + '\t' + m_pointer + '\t' + str(hex2dec(to_big_endian(o_pointer))) + '\t' + str(hex2dec(to_big_endian(m_pointer))) + '\t' + str(hex2dec(to_big_endian(m_pointer)) - hex2dec(to_big_endian(o_pointer)))
				f0.write(aaa + '\t' + str(pointers_table[o_pointer]) + '\n')
				f0.close()	
				"""
			
				pointers_modified += 1
				
				for address in pointers_table[o_pointer]:
					
					if is_valid_address(address):
						
						if is_in_text_block(address):
							new_addresses = pointer_finder(f2, o_pointer, start=TEXT_BLOCK_START, previous_seek=None)
							if new_addresses:
								for new_address in new_addresses:
									f2.seek(new_address)			
									f2.write(HexToByte(m_pointer))
								
						if not is_in_text_block(address):
							f2.seek(address)
							f2.write(HexToByte(m_pointer))

					else:
						pass
			else:
				pass
			## end - text repointer process
			
		else:
			sys.exit('DRAMATIC ERROR! ' + o_pointer + 'pointer not found in pointers table')
else:
	sys.exit('DRAMATIC ERROR! array of original pointers is not alligned with the array of modified pointers')

	
## start - shop repointer 2
shop_address_not_modified = 0
for shop_pointer in shop_pointers.keys():
	if shop_pointers.get(shop_pointer):
		pointers_modified += 1
		for address in shop_pointers.get(shop_pointer):
			if is_shop_pointer(address):
				f2.seek(address)
				f2.write(HexToByte(shop_pointer))
			else:
				#print dec2hex(address)
				shop_address_not_modified += 1
	else:
		pass
## end - shop repointer 2

"""
pointers_found = []
f.seek(TEXT_BLOCK_START)
while True:
	address = f.find(HexToByte('faff'), f.tell())
	if (address==-1):
		break
	else:
		f.seek(address + 2)
		pointer = ByteToHex(f.read(3))
		pointers_found.append(address)
		print dec2hex(address + 0x02) + ' - ' + pointer + ' - ' + str(pointers_table.get(pointer))
		
		f3.seek(TEXT_BLOCK_START)
		address2 = f3.find(HexToByte(pointer), f3.tell())
		if address2:
			print dec2hex(address2)
"""	



## start - statistics
print 'indirizzi shop non modificati: ' + str(shop_address_not_modified)

print 'puntatori totali: ' + str(len(pointers_table))

"""
addresses_found = 0
for addresses in pointers_table:
	if addresses:
		addresses_found += len(addresses)
print 'indirizzi totali: ' + str(addresses_found)
"""

print 'indirizzi modificati: ' + str(pointers_modified)
print 'puntatori non trovati: ' + str(pointers_not_found_counter)
## end - statistics

# chiusura delle mmap della rom ORIGINALE e della rom MODIFICATA
f.close()
f2.close()