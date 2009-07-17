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
		self.table_newline = None
		self.table_breakline = None
		
		## tbl parser
		f = open(filename, "r")
		for line in f:
			if not line.startswith(Table.COMMENT_CHAR):
			
				if line.startswith(Table.NEWLINE_CHAR):
					"""
					if self._table_newline:
						sys.exit('two new line found!')
					"""
					self.table_newline = line[1:len(line)]
					self._table[int(line[1:len(line)], 16)] = "{END}\n\n"
				if line.startswith(Table.BREAKLINE_CHAR):
					"""
					if self._table_breakline:
						sys.exit('two break line found!')
					"""
					self.table_breakline = line[1:len(line)]
					self._table[int(line[1:len(line)], 16)] = "\n"
		
				pair = line.strip("\n").split("=")
				if len(pair[0]) == 2:
					self._table[int(pair[0], 16)] = pair[1]
				if len(pair[0]) > 2:
					pass #mte
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
			if len(self.get(key)) == 2 and not '\n' in self.get(key):
				return True
			else:
				return False
		else:
			return None

	def find(self, value):
		k = None
		for key in self._table.keys():
			if self._table.get(key) == value:
				if k:
					#print value
					raise Exception, "two instance of " + value + " found!"
				k = key
		return k