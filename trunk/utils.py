def dec2hex(n):
	""" return the hexadecimal string representation of an integer """
	hex = None
	if type(n) == type(1):
		hex = "%x" % n
	return hex
	
def hex2dec(s):
	""" return the integer value of a hexadecimal string s """
	return int(s, 16)
		
def int2byte(n):
	""" return a string value of a int value """
	return chr(n)

def byte2int(b):
	"""  """
	return ord(b)
	
def readed_to_int(readed):
	"""  """
	integer = 0
	for x in readed:
		integer = (integer << 8) | ord(x)
	return integer

def to_little_endian(p):
	"""  """
	pointer = p[4:6] + p[2:4] + 'd7'
	return pointer
	
def to_big_endian(p):
	"""  """
	pointer = 'd7' + p[2:4] + p[0:2]
	return pointer