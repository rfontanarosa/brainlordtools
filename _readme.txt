import zlib
thevalueyouwant = zlib.crc32(open(filepath,'rb').read())

history:
	2008-10-07 (0.44)
		added two constant TEXT_BLOCK_SIZE e TEXT_BLOCK_MAX_SIZE
		added function int2byte
	2008-09-25 (0.43)
		added two forced closure in the repointer alghorithm
		rewrote the description of the alghorithm
		added an if block to check if a original pointer is in the pointers table in the alghorithm
		added some comments
		renamed some variables
	2008-09-24 (0.42)
		FIXED A HUGE BUG in pointer_finder function. now the search restart correctrly using f.seek(address + 1)
		added a check named in_range in the OPTIONAL parameters of pointer_finder
		removed useless function make_a_doc
		FIXED A BUG: added is_valid_address check in pointer_finder function
		added a procedure that repoint also the text of shops
		changed some todos
	2008-09-23 (0.36)
		renamed deswitched_pointer in to_big_endian e switched_pointer in to_little_endian
		added FAERIES_POINTER_START_BYTE variable
	2008-09-22 (0.35)
		renamed TEXT_POINTER3 to FAERIES_POINTER and fixed the FAERIES_POINTER_BLOCK_START
	2008-09-19 (0.34)
		improved the repointer algorithm
		now the function get_pointers accept the text after double f7 bytes as an address to repointer
		found another pointer text block and
		added some statistics and screen error messages
	2008-09-18 (0.33)
		added a counter for the repointered pointers
		new get_pointers_table function!
		improved repointer algorithm (but at the end of the presentation the rom crash)
		renamed functions: hex2dec (hex_to_int), dec2hex (int_to_hex)
	2008-09-17 (0.31)
		TEXT_POINTER2_BLOCK_END fixed
		a lot of tests
	2008-09-16 (0.3)
		partial repointer algorithm (with documentation)
		the addresses of the function get_pointers_table now are stored as an integer
		function deswitched_pointer added!
		function make_a_doc added!
		function hex_to_int added!
	2008-09-15 (alpha)
		initial alpha
"""