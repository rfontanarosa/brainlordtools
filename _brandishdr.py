__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, shutil, urlparse

from _rhtools.utils import byte2int
from _falcomtools.falcom_decompress_v2 import decompress_FALCOM3
from _falcomtools.falcom_compress_v2 import compress_FALCOM3

act_path = './resources/brandishdr/source/PSP_GAME/USERDIR/data/pa/'
script_path = './resources/brandishdr/source/PSP_GAME/USERDIR/data/script/'
txt_path = './resources/brandishdr/source/PSP_GAME/USERDIR/data/txt/item.tb'

dump_path = './resources/brandishdr/dump/'
translation_path = './resources/brandishdr/translation/'

dump_path1 = './resources/brandishdr/dump1/'
dump_path2 = './resources/brandishdr/dump2/'

unpack_act = True
pack_act = True
extract_scripts = True
extract_items = True

insert_items = True

def char2hex(char):
	integer = int(char.encode('hex'), 16)
	return hex(integer)

if unpack_act:
		st_de_act_path = urlparse.urljoin(dump_path, 'st_de.act/')
		shutil.rmtree(st_de_act_path, ignore_errors=True)
		os.mkdir(st_de_act_path)
		act_file_path = urlparse.urljoin(act_path, 'st_de.act')
		with open(act_file_path, 'rb') as f1, open(act_file_path, 'rb') as f2:
			block = f1.read(16)
			files = byte2int(block[0])
			for File in range(files):
				filename = f1.read(16)
				file_offset = f1.read(4)
				file_compressed_size = f1.read(4)
				file_original_size = f1.read(4)
				f1.read(4)
				offset = struct.unpack('i', file_offset)[0]
				compressed_size = struct.unpack('i', file_compressed_size)[0]
				original_size = struct.unpack('i', file_original_size)[0]
				f2.seek(offset)
				file_content = f2.read(compressed_size)
				with open(urlparse.urljoin(st_de_act_path, filename.rstrip('\0')), 'wb') as out:
					if original_size == 0:
						out.write(file_content)
					else:
						out.write(decompress_FALCOM3(file_content))

if extract_items:
	item_tb_path = urlparse.urljoin(dump_path, 'item.tb/')
	shutil.rmtree(item_tb_path, ignore_errors=True)
	os.mkdir(item_tb_path)
	item_file_path = './resources/brandishdr/source/PSP_GAME/USERDIR/data/txt/item.tb'
	with open(item_file_path, 'rb') as f:
		filesize = os.stat(f.name).st_size
		i = 0
		while f.tell() != filesize:
			block = f.read(188)
			id = block[:4]
			name = block[4:32+4]
			description = block[36:128+36]
			other = block[164:]
			with open(urlparse.urljoin(item_tb_path, '%s.txt' % str(i).zfill(3)), 'wb') as out:
				out.write(id)
				out.write(name)
				out.write(description)
				out.write(other)
			i += 1

if insert_items:
	item_file_path_t = './resources/brandishdr/translated/PSP_GAME/USERDIR/data/txt/item.tb'
	with open(item_file_path_t, 'wb') as out:
		path = urlparse.urljoin(translation_path, 'item.tb/')
		files = sorted(os.listdir(path))
		for file in files:
			with open(urlparse.urljoin(path, file), 'rb') as f:
				block = f.read(188)
				out.write(block)

if extract_scripts:

	shutil.rmtree(dump_path1, ignore_errors=True)
	shutil.rmtree(dump_path2, ignore_errors=True)
	os.mkdir(dump_path1)
	os.mkdir(dump_path2)

	# 04:text; 3c:shop; 78:video; 21:?; 47:name

	k1 = k2 = 1
	files = os.listdir(script_path)

	for file in files:

		commands = {}
		with open(script_path + file, 'rb') as f:

			filesize = os.stat(f.name).st_size
			f.seek(0x28)
			n = f.read(2)
			n = struct.unpack('h', n)[0]
			textsize = f.read(2)
			textsize = struct.unpack('h', textsize)[0]
			end = filesize - textsize
			start = end - (n * 32)

			""" METHOD1 - POINTER TABLE """

			i = 0
			f.seek(start)
			while f.tell() != end:
				paddress = f.tell()
				block = f.read(32)
				opcode = block[:1]
				opcode = ord(opcode)
				command = (paddress, block)
				if opcode not in commands:
					commands[opcode] = list()
				commands[opcode].append(command)
				i +=  1

			opcodes = (0x04, 0x21, 0x78, 0x3c)
			for opcode in opcodes:
				if opcode in commands:
					for command in commands[opcode]:
						offset = command[1][20:22]
						offset = struct.unpack('h', offset)[0]
						paddress = command[0]
						#length = command[1][23:25]
						#length = struct.unpack('>h', length)[0]
						f.seek(end + offset)
						#text = f.read(length)
						text = b''
						b = b''
						while b != chr(0x00):
							text += b
							b = f.read(1)
						length = len(text)
						with open(dump_path1 + '%s - %s - %s - %s - %i.txt' % (file, str(k1).zfill(3), hex(paddress)[:-1], hex(offset), length), 'w') as out:
							out.write(text)
						k1 += 1

			""" METHOD2 - TEXT """

			f.seek(end)
			text = b''
			t_address = f.tell() - end
			while(f.tell() < filesize):
				b = f.read(1)
				if b == chr(0xcc):
					t_address += 1
				text += b
				if ord(b) == 0x00:
					length = len(text)
					with open(dump_path2 + '%s - %s - %s - %i.txt' % (file, str(k2).zfill(3), hex(t_address)[:-1], length), 'w') as out:
						out.write(text)
					t_address = f.tell() - end
					text = b''
					k2 += 1
