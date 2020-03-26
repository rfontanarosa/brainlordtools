__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, string, re, operator
from utils import hex2dec, int2byte, hex2byte, byte2int, int_to_bytes
from collections import OrderedDict

class Table():

    COMMENT_CHAR = ';'
    NEWLINE_CHAR = '/'
    BREAKLINE_CHAR = '*'
    PATTERN_SEPARATED_BYTE = '{%s}'

    def __init__(self, filename):

        self._table = OrderedDict()
        self._mte = OrderedDict()
        self._dict = OrderedDict()
        self._newline = None
        self._breakline = None
        self._comments = []

        self._reverse_table = None
        self._reverse_mte = None
        self._reverse_dict = None

        ## parser
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip('\n')
                # comment-line
                if line.startswith(Table.COMMENT_CHAR):
                    self._comments.append(line[1:])
                else:
                    if '=' in line:
                        parts = line.partition('=')
                        part_key = parts[0]
                        part_value = parts[2].replace('\r', '').replace('\n', '')
                        if part_value:
                            if len(part_key) == 4:
                                key = hex2dec(part_key[:2])
                                subkey = hex2dec(part_key[2:])
                                if key not in self._dict:
                                    self._dict[key] = OrderedDict()
                                self._dict[key][subkey] = part_value
                            else:
                                key = hex2dec(part_key)
                                if len(part_value) > 1:
                                    self._mte[key] = part_value
                                else:
                                    self._table[key] = part_value
                    # new-line
                    elif line.startswith(Table.NEWLINE_CHAR):
                        self._newline = int(line[1:], 16)
                        self._table[int(line[1:], 16)] = '\r'
                    # break-line
                    elif line.startswith(Table.BREAKLINE_CHAR):
                        self._breakline = int(line[1:len(line)], 16)
                        self._table[int(line[1:len(line)], 16)] = '\n'
            # init reverse
            self._initReverseTable()
            self._initReverseMte()
            self._initReverseDictionary()

    def __iter__(self):
        return self._table.__iter__()

    def __str__(self):
        return self._table.__str__()

    def __len__(self):
        return len(self._table)

    def __getitem__(self, key):
        return self._table.__getitem__(key)

    def __contains__(self, key):
        return self._table.__contains__(key)

    def get(self, key):
        return self._table.get(key)

    def separateByteEncode(self, text):
        decoded = b''
        if (text):
            iter = enumerate(text)
            for i, byte in iter:
                decoded += self.PATTERN_SEPARATED_BYTE % byte.encode('hex_codec')
        return decoded

    def encode(self, text, mte_resolver=True, dict_resolver=True, cmd_list=[]):
        decoded = b''
        if (text):
            iter = enumerate(text)
            for i, byte in iter:
                key = byte2int(byte)
                if self.isNewline(key):
                    decoded += self.PATTERN_SEPARATED_BYTE % byte.encode('hex_codec')
                elif self.isBreakline(key):
                    decoded += '\n'
                else:
                    if key in cmd_list:
                        bytes = byte + iter.next()[1]
                        subkey = byte2int(bytes[1])
                        decoded += self.PATTERN_SEPARATED_BYTE % bytes[0].encode('hex_codec')
                        decoded += self.PATTERN_SEPARATED_BYTE % bytes[1].encode('hex_codec')
                    elif dict_resolver and key in self._dict:
                        bytes = byte + iter.next()[1]
                        subkey = byte2int(bytes[1])
                        if subkey in self._dict[key]:
                            decoded += self._dict[key][subkey]
                        else:
                            decoded += self.PATTERN_SEPARATED_BYTE % bytes[0].encode('hex_codec')
                            decoded += self.PATTERN_SEPARATED_BYTE % bytes[1].encode('hex_codec')
                    elif mte_resolver and key in self._mte:
                        decoded += self._mte[key]
                    elif key in self._table:
                        decoded += self[key]
                    else:
                        decoded += self.PATTERN_SEPARATED_BYTE % byte.encode('hex_codec')
        return decoded

    def decode(self, text, mte_resolver=True, dict_resolver=True):
        decoded = b''
        if (text):
            if dict_resolver:
                for value in sorted(self._reverse_dict, key=len, reverse=True):
                    if value in text:
                        key = int_to_bytes(self._reverse_dict[value])
                        h1 = self.PATTERN_SEPARATED_BYTE % key[0].encode('hex_codec')
                        h2 = self.PATTERN_SEPARATED_BYTE % key[1].encode('hex_codec')
                        h1 = h1[:2] + '-' + h1[2:]
                        h2 = h2[:2] + '-' + h2[2:]
                        text = text.replace(value, h1+h2)
            if mte_resolver:
                #for value in sorted(self._reverse_mte, key=operator.itemgetter(1), reverse=True):
                for value in sorted(self._reverse_mte, key=len, reverse=True):
                    if value in text:
                        key = int2byte(self._reverse_mte[value])
                        h = self.PATTERN_SEPARATED_BYTE % key.encode('hex_codec')
                        h = h[:2] + '-' + h[2:]
                        text = re.sub(r'(?!%s)(%s)(?!%s)' % (self.PATTERN_SEPARATED_BYTE[0], re.escape(value), self.PATTERN_SEPARATED_BYTE[-1]), h, text)
            i = 0
            while i < len(text):
                byte = text[i]
                if byte == '{':
                    byte_to_decode = b''
                    while byte != '}':
                        i += 1
                        byte = text[i]
                        if byte != '}' and byte != '-':
                            byte_to_decode += byte
                    byte_decoded = self._reverse_table.get(byte_to_decode)
                    if not byte_decoded:
                        try:
                            byte_decoded = '%s' % byte_to_decode.decode('hex_codec')
                        except TypeError:
                            raise TypeError
                    else:
                        byte_decoded = hex2byte(format(byte_decoded, 'x'))
                    decoded += byte_decoded
                else:
                    key = self._reverse_table.get(byte)
                    if key != None:
                        decoded += int2byte(key)
                    else:
                        decoded += byte
                i += 1
        return decoded

    def isMTE(self, key):
        """ Check if the element is a MTE (Multi Tile Encoding) """
        return self.get(key) and len(self.get(key)) >= 2 and not self.isNewline(key) and not self.isBreakline(key)

    def getMTEs(self):
        """  """
        return self._mte

    def isNewline(self, key):
        return self._newline == key

    def isBreakline(self, key):
        return self._breakline == key

    def getNewline(self):
        return self._newline

    def getBreakline(self):
        return self._breakline

    def getComments(self):
        return self._comments

    def _initReverseTable(self):
        if not self._reverse_table:
            self._reverse_table = dict((v,k) for k,v in self._table.iteritems())

    def _initReverseMte(self):
        if not self._reverse_mte:
            self._reverse_mte = OrderedDict()
            for key in self._mte:
                self._reverse_mte[self._mte[key]] = key

    def _initReverseDictionary(self):
        if not self._reverse_dict:
            self._reverse_dict = {}
            for key in self._dict:
                for subkey in self._dict[key]:
                    rkey = (key * 0x100) + subkey
                    self._reverse_dict[self._dict[key][subkey]] = rkey
