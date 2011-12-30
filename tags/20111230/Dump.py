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
	#todo anche end deve essere None
	def extract(f, end, start=0, previous_seek=None):
		""" extract a block extracted from a file """
		if start > end:
			raise Exception, "Start address must be lower than end address!"
		f.seek(start)
		
		if previous_seek:
			f.seek(previous_seek)
		
		return f.read((end - start)+1)

	@staticmethod
	def insert(f, dump, end, start=0):
		""" insert a block inside a file """
		if len(dump) > ((end - start)+1):
			raise Exception, "Dump size is too large and it can't be inserted!"
		else:
			f.seek(start)
			f.write(dump)
		"""
		while(f.tell() < end):
			f.write("0")
		"""
		
	def __init__(self, dump=""):
		self._dump = dump
		
	def __len__(self):
		return len(self._dump)
		
	def __cmp__ (self, dump):
		if not isinstance(dump, Dump):
			raise TypeError, "Illegal argument type for built-in operation!"
		return self._dump == dump.getDump()
		
	def getDump(self):
		return self._dump
		
	def fromTxt(self, table=None, filename="dump2.txt", separated_byte_format=True):
		"""  """
		with open(filename, "rb") as f:
			if table:
				#print separated_byte_format
				if separated_byte_format:
					while True:
						byte = f.read(1)
						if not byte:
							break
						if byte == "\n":
							self._dump += int2byte(table.getBreakline())			
						elif byte == "{":
							while "}" not in byte:
								byte += f.read(1)
							if byte == "{END}":
								f.read(2)
								self._dump += int2byte(table.getNewline())
							else:
								if table.find(byte[1:len(byte)-1]):
									self._dump += int2byte(table.find(byte[1:len(byte)-1]))
								else:
									self._dump += HexToByte(byte[1:len(byte)-1])
						else:
							found = table.find(byte)
							if found:
								self._dump += int2byte(found)
							else:
								self._dump += byte
				else:
					while True:
						byte = f.read(1)
						found = table.find(byte)
						if found:
							self._dump += int2byte(found)
						else:
							self._dump += byte
						if not byte:
							break
			else:
				#todo
				pass

	def toTxt(self, table=None, filename="dump.txt", separated_byte_format=True):
		"""  """
		with open(filename, "wb") as f:
			if table:
				for byte in self._dump:
					if table.get(byte2int(byte)):
						if separated_byte_format and table.isDTE(byte2int(byte)):
							f.write("{%s}" % table.get(byte2int(byte)))
						else:
							f.write(table.get(byte2int(byte)))
					else:
						f.write("{%s}" % ByteToHex(byte))
			else:
				f.write(self._dump)