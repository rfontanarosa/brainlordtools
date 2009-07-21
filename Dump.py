__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit("missing HexByteConversion module!")

from utils import dec2hex, hex2dec, int2byte, byte2int

class Dump():
	
	@staticmethod
	def extract(f, start, end):
		""" extract a block from a file creating a block """
		f.seek(start)
		return f.read((end - start)+1)
		
	def __init__(self, dump=""):
		self._dump = dump
		
	def __len__(self):
		return len(self._dump)
		
	def __cmp__ (self, dump):
		return self._dump == dump.getDump()
		
	def getDump(self):
		return self._dump
		
	def fromTxt(self, table=None, filename="dump.txt", separated_byte_format=True):
		f = open(filename, "r")
		
		if separated_byte_format:
			while True:
			
				byte = f.read(1)
				
				if not byte:
					break
				
				if byte == "{":
					while "}" not in byte:
						byte += f.read(1)
					if byte == "{END}":
						byte += f.read(2)
						self._dump += int2byte(table.find(byte))
					else:
						if dec2hex(table.find(byte[1:len(byte)-1])):
							self._dump += int2byte(table.find(byte[1:len(byte)-1]))
						else:
							self._dump += HexToByte(byte[1:len(byte)-1])
				else:
					self._dump += int2byte(table.find(byte))
					
		else:
			pass
		f.close()

	def toTxt(self, table=None, filename="dump.txt", separated_byte_format=True):
		"""  """
		out = open(filename, "w")
		if table:
			for byte in self._dump:
				if table.get(byte2int(byte)):
					if separated_byte_format and table.isDTE(byte2int(byte)):
						out.write("{%s}" % table.get(byte2int(byte)))
					else:
						out.write(table.get(byte2int(byte)))
				else:
					out.write("{%s}" % ByteToHex(byte))
		else:
			out.write(text_extracted)
		out.close()