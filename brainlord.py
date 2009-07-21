__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

# TODO trovare un modo per verificare se e presente o meno l'header
# TODO aggiungere agli indirizzi i byte dell'header SE questo e presente
TEXT_BLOCK_START = 0x170000
TEXT_BLOCK_END = 0x17fac9
TEXT_BLOCK_LIMIT = 0x17ffff
TEXT_BLOCK_SIZE = (TEXT_BLOCK_END - TEXT_BLOCK_START) + 1
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

TEXT_POINTER1_BLOCK_START = 0xf9e
TEXT_POINTER1_BLOCK_END = 0xfef

TEXT_POINTER2_BLOCK_START = 0x50010
TEXT_POINTER2_BLOCK_END = 0x55567

## there are 20 (?) pointers in this block and every pointer starts with 0x01
#FAERIES_POINTER_START_BYTE = 0x01
FAERIES_POINTER_BLOCK_START = 0x18ea0
FAERIES_POINTER_BLOCK_END = 0x18f9b