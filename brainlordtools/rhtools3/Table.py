__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, re
from collections import OrderedDict

class Table():

    COMMENT_CHAR = ';'
    NEWLINE_CHAR = '/'
    BREAKLINE_CHAR = '*'
    PATTERN_SEPARATED_BYTE = '{{{:02x}}}'

    def __init__(self, filename):

        self._newline = None
        self._breakline = None
        self._comments = []

        self._table = OrderedDict()
        self._mte = OrderedDict()
        self._dict = OrderedDict()

        self._reverse_table = None
        self._reverse_mte = None
        self._reverse_dict = {}

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip('\n')
                if line.startswith(Table.COMMENT_CHAR):
                    self._comments.append(line[1:])
                else:
                    if '=' in line:
                        parts = line.partition('=')
                        part_key = parts[0]
                        part_value = parts[2].replace('\r', '').replace('\n', '')
                        if part_value:
                            if len(part_key) == 4:
                                key = int(part_key[:2], 16)
                                subkey = int(part_key[2:], 16)
                                if key not in self._dict:
                                    self._dict[key] = OrderedDict()
                                self._dict[key][subkey] = part_value
                                self._reverse_dict[part_value] = (key, subkey)
                            else:
                                key = int(part_key, 16)
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
            self._reverse_table = {v: k for k, v in self._table.items()}
            self._reverse_mte = OrderedDict({v: k for k, v in self._mte.items()})
            self._reverse_mte_keys = sorted(self._reverse_mte, key=len, reverse=True)
            self._reverse_dict_keys = sorted(self._reverse_dict, key=len, reverse=True)

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
                decoded += self.PATTERN_SEPARATED_BYTE.format(byte)
        return decoded

    def decode(self, text, mte_resolver=True, dict_resolver=True, cmd_list=None):
        """ decode bytes into string """
        decoded = []
        if text:
            i = 0
            while i < len(text):
                byte = text[i]
                if self.isNewline(byte):
                    decoded.append(self.PATTERN_SEPARATED_BYTE.format(byte))
                elif self.isBreakline(byte):
                    decoded.append('\n')
                else:
                    if cmd_list and byte in cmd_list.keys():
                        decoded.append(self.PATTERN_SEPARATED_BYTE.format(byte))
                        bytes_to_read = cmd_list.get(byte)
                        for _ in range(bytes_to_read):
                            i += 1
                            byte = text[i]
                            decoded.append(self.PATTERN_SEPARATED_BYTE.format(byte))
                    elif dict_resolver and byte in self._dict:
                        i += 1
                        byte2 = text[i]
                        if byte2 in self._dict[byte]:
                            decoded.append(self._dict[byte][byte2])
                        else:
                            decoded.append(self.PATTERN_SEPARATED_BYTE.format(byte))
                            decoded.append(self.PATTERN_SEPARATED_BYTE.format(byte2))
                    elif mte_resolver and byte in self._mte:
                        decoded.append(self._mte[byte])
                    elif byte in self._table:
                        decoded.append(self._table[byte])
                    else:
                        decoded.append(self.PATTERN_SEPARATED_BYTE.format(byte))
                i += 1
        return ''.join(decoded)

    def encode(self, text, mte_resolver=True, dict_resolver=True):
        """ encode string into bytes """
        encoded = b''
        if text:
            if dict_resolver:
                for value in self._reverse_dict_keys:
                    if value in text:
                        key = self._reverse_dict[value]
                        h1 = self.PATTERN_SEPARATED_BYTE.format(key[0])
                        h2 = self.PATTERN_SEPARATED_BYTE.format(key[1])
                        text = text.replace(value, h1 + h2)
            if mte_resolver:
                for value in self._reverse_mte_keys:
                    if value in text:
                        key = self._reverse_mte[value]
                        h = self.PATTERN_SEPARATED_BYTE.format(key)
                        text = re.sub(r'(?!{})({})(?!{})'.format(self.PATTERN_SEPARATED_BYTE[0], re.escape(value), self.PATTERN_SEPARATED_BYTE[-1]), h, text)
            i = 0
            while i < len(text):
                char = text[i]
                if char == self.PATTERN_SEPARATED_BYTE[0]:
                    char_to_decode = text[i+1:i+3]
                    byte_decoded = bytes.fromhex(char_to_decode)
                    encoded += byte_decoded
                    i += 3
                else:
                    key = self._reverse_table.get(char)
                    if key != None:
                        encoded += bytes([key])
                    else:
                        encoded += char.encode()
                i += 1
        return encoded

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
