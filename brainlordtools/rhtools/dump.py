import os

def dump_gfx(f, start, end, dump_path, filename):
	f.seek(start)
	block_size = end - start
	block = f.read(block_size)
	with open(os.path.join(dump_path, filename), 'wb') as gfx_file:
		gfx_file.write(block)

def insert_gfx(f, start, end, translation_path, filename):
	with open(os.path.join(translation_path, filename), 'rb') as f1:
		block = f1.read()
		if len(block) == end - start:
			f.seek(start)
			f.write(block)
		else:
			raise Exception('GFX file - Different size')
