__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

from .HexByteConversion import HexToByte

def byte2int(b):
	""" returns an integer representing a 8-bit string """
	return ord(b)

def int2byte(n):
	""" convert an integer to a byte """
	return chr(n)

def int2hex(n):
	""" convert an integer number to a hexadecimal string """
	return hex(n).rstrip('L')

def hex2byte(h):
	return HexToByte(h)

def hex2dec(s):
	""" convert a hexadecimal string to an integer """
	return int(s, 16)

def int_to_bytes(i):
	"""  """
	import binascii
	hex_string = '%x' % i
	n = len(hex_string)
	return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

def string_address2int_address(s, switch=False, offset=0):
	"""  """
	if (switch):
		n = byte2int(s[0]) + (byte2int(s[1]) << 8) + offset
	else:
		n = (byte2int(s[0]) << 8) + byte2int(s[1]) + offset
	return n

def int_address2string_address(n, switch=False, shift=0):
	"""  """
	import binascii
	h = int2hex(n)
	s = binascii.unhexlify(h[shift:])
	if (switch):
		s = s[1] + s[0]
	return s

def int_address2string_address2(n, switch=False, shift=0):
	"""  """
	import binascii
	h = int2hex(n)
	unhex = h[shift:]
	if len(unhex) % 2 != 0:
		unhex = '0' + unhex
	s = binascii.unhexlify(unhex)
	if (switch):
		s = s[1] + s[0]
	return s

def clean_text(text):
	"""  """
	import re
	replaced = re.sub('{..}', '\n', text)
	return replaced

########
# TEST #
########

import unittest

class TestUtils(unittest.TestCase):

	def setUp(self):
		pass

	def test_byte2int(self):
		self.assertEqual(byte2int('a'), 97)

	def test_int2byte(self):
		self.assertEqual(int2byte(97), 'a')

	def test_int2hex(self):
		self.assertEqual(int2hex(97), '0x61')

	def test_hex2byte(self):
		self.assertEqual(hex2byte('61'), 'a')

	def test_hex2dec(self):
		self.assertEqual(hex2dec('61'), 97)

if __name__ == '__main__':
	unittest.main()
