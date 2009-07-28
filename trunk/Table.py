__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

class Table():

	COMMENT_CHAR = ";"
	NEWLINE_CHAR = "/"
	BREAKLINE_CHAR = "*"

	def __init__(self, filename):
		
		__name__ = "Table"
		
		self._table = {}
		self._newline = None
		self._breakline = None
		
		## tbl parser
		f = open(filename, "r")
		
		for line in f:
		
			if not line.startswith(Table.COMMENT_CHAR):

				if line.startswith(Table.NEWLINE_CHAR):
					self._newline = int(line[1:len(line)], 16)
					self._table[int(line[1:len(line)], 16)] = "{END}\n\n"

				if line.startswith(Table.BREAKLINE_CHAR):
					self._breakline = int(line[1:len(line)], 16)
					self._table[int(line[1:len(line)], 16)] = "\n"

				if "=" in line:
					pair = line.strip("\n").split("=")
					self._table[int(pair[0], 16)] = pair[1]

		f.close()

	def __iter__(self):
		return self._table.iteritems()

	def __str__(self):
		return self._table.__str__()
		
	def __len__(self):
		return len(self._table)

	def get(self, key, default=None):
		try:
			return self.__getitem__(key)
		except:
			return default

	def __getitem__(self, key):
		return self._table.get(key)
		
	def __contains__(self, key):
		try:
			self.__getitem__(key)
			return True
		except KeyError:
			return False
	
	def has_key(self, key):
		return self.__contains__(key)

	def isDTE(self, key):
		""" check if the element is a DTE """	
		if self.has_key(key):
			return len(self.get(key)) >= 2 and not self.isNewline(key) and not self.isBreakline(key):
		else:
			return None

	def isNewline(self, key):
		return self._newline == key

	def isBreakline(self, key):
		return self._breakline == key
			
	def find(self, value):
		k = None
		for key in self._table.keys():
			if self._table.get(key) == value:
				if k:
					#print value
					raise Exception, "two instance of " + value + " found!"
				k = key
		return k