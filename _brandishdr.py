__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, shutil, csv

from _rhtools.utils import byte2int
from _falcomtools.falcom_decompress_v2 import decompress_FALCOM3
from _falcomtools.falcom_compress_v2 import compress_FALCOM3

resources_path = './resources/brandishdr/'
data_path = os.path.join(resources_path, 'source/PSP_GAME/USERDIR/data/')
translated_data_path = os.path.join(resources_path, 'translated/PSP_GAME/USERDIR/data/')
dummy_path = './resources/brandishdr/dummy/'


unpack_act = True
pack_act = True

extract_items = True
insert_items = True

extract_scripts = True

def char2hex(char):
	integer = int(char.encode('hex'), 16)
	return hex(integer)

if unpack_act:
	dump_path = os.path.join(resources_path, 'dump', 'st_de.act/')
	shutil.rmtree(dump_path, ignore_errors=True)
	os.mkdir(dump_path)
	file_path = os.path.join(data_path, 'pa', 'st_de.act')
	with open(file_path, 'rb') as f1, open(file_path, 'rb') as f2:
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
			with open(os.path.join(dump_path, filename.rstrip('\0')), 'wb') as out:
				if original_size == 0:
					out.write(file_content)
				else:
					out.write(decompress_FALCOM3(file_content))
			with open(os.path.join(dump_path, 'filelist.csv'), 'a') as out:
				csv_writer = csv.writer(out)
				csv_writer.writerow([filename.rstrip('\0'), offset, compressed_size, original_size])

if extract_items:
	dump_path = os.path.join(resources_path, 'dump', 'item.tb/')
	shutil.rmtree(dump_path, ignore_errors=True)
	os.mkdir(dump_path)
	file_path = os.path.join(data_path, 'txt', 'item.tb')
	with open(file_path, 'rb') as f:
		filesize = os.stat(f.name).st_size
		i = 0
		while f.tell() != filesize:
			block = f.read(188)
			id = block[:4]
			name = block[4:32+4]
			description = block[36:128+36]
			other = block[164:]
			with open(os.path.join(dump_path, '%s.txt' % str(i).zfill(3)), 'wb') as out:
				out.write(id)
				out.write(name)
				out.write(description)
				out.write(other)
			i += 1

if insert_items:
	translated_file_path = os.path.join(translated_data_path, 'txt', 'item.tb')
	with open(translated_file_path, 'wb') as out:
		translation_path = os.path.join(resources_path, 'translation', 'item.tb/')
		files = sorted(os.listdir(translation_path))
		for File in files:
			with open(os.path.join(translation_path, File), 'rb') as f:
				block = f.read(188)
				out.write(block)

if extract_scripts:

	script_path = os.path.join(data_path, 'script/')
	dump_path1 = './resources/brandishdr/dump1/'
	dump_path2 = './resources/brandishdr/dump2/'

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
