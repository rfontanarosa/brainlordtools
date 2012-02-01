__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys
from utils import *

def apply(file, patch):
	with open(patch, 'rb') as f:
		header = f.read(5)
		if header == 'PATCH':
			roffset = f.read(3)
			while roffset != 'EOF':
				rsize = f.read(2)
				offset = byte32int(roffset)
				size = byte22int(rsize)
				data = f.read(size)
				with open(file, 'r+b') as f2:
					f2.seek(offset)
					f2.write(data)
				roffset = f.read(3)
		else:
			sys.exit('Not valid!')
			
			
def create(file1, file2, patch):
	with open(patch, 'wb') as f:
		f.write('PATCH')
		with open(file1, 'rb') as f2:		
			with open(file2, 'rb') as f3:
				b = f2.read()
				while b:
					b = f2.read()
					
apply('roms/Brandish (U) [!] - Copy.smc', 'roms/BRANDI~2.IPS')
create('roms/Brandish (U) [!].smc', 'roms/Brandish (U) [!] - Copy.smc', 'roms/BRANDI~3.IPS')