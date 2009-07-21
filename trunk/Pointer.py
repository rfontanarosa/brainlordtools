__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

class Pointer():

	def __init__(self, pointer):
		self._pointer = pointer
		self._positions = []

	def __len__(self):
		return len(self._positions)
		
	def __str__(self):
		return str(self._pointer)