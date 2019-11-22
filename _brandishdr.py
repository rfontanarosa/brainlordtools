__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, shutil

scripts_path = './resources/brandishdr/sources/scripts/'
dump_path1 = './resources/brandishdr/dump1/'
dump_path2 = './resources/brandishdr/dump2/'

shutil.rmtree(dump_path1, ignore_errors=True)
shutil.rmtree(dump_path2, ignore_errors=True)
os.mkdir(dump_path1)
os.mkdir(dump_path2)

# 04:text; 3c:shop; 78:video; 21:?; 47:name

k1 = k2 = 1
files = os.listdir(scripts_path)

for file in files:

	commands = {}
	with open(scripts_path + file, 'rb') as f:

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
