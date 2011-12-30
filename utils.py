def int2byte(n):
	""" convert an integer to a byte """
	return chr(n)

def byte2int(b):
	""" returns an integer representing a 8-bit string """
	return ord(b)

def int2hex(i):
	""" convert an integer number to a hexadecimal string """
	return hex(i)

def hex2dec(s):
	""" convert a hexadecimal string to an integer """
	return int(s, 16)

def to_little_endian(p):
	"""  """
	pointer = p[4:6] + p[2:4] + 'd7'
	return pointer
	
def to_big_endian(p):
	"""  """
	pointer = 'd7' + p[2:4] + p[0:2]
	return pointer

def switch_byte(p):
	"""  """
	return p[2:4] + p[0:2]

def string_address2int_address(s, switch=False, offset=0):
	"""  """
	if (switch):
		i = byte2int(s[0]) + (byte2int(s[1]) << 8) + offset
	else:
		i = (byte2int(s[0]) << 8) + byte2int(s[1]) + offset
	return i

def test():
	s = "a"
	i = 97
	h = "61"
	print byte2int(s) == i
	print int2byte(i) == s
	print hex2dec(h) == i