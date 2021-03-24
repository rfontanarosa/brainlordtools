__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, re
from collections import OrderedDict

class Table():

    COMMENT_CHAR = ';'
    # EOS_CHAR = '/'
    EOL_CHAR = '*'

    HEX_FORMAT = '{{{:02x}}}'
    DOUBLE_HEX_FORMAT =  HEX_FORMAT + HEX_FORMAT

    def __init__(self, filename):

        self._eos = None
        self._eol = None
        self._comments = []

        self._table = OrderedDict()
        self._mte = OrderedDict()
        self._dict = OrderedDict()

        self._reverse_table = OrderedDict()
        self._reverse_mte = OrderedDict()
        self._reverse_dict = OrderedDict()

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip('\r\n').replace('\\n', '\n')
                if line.startswith(Table.COMMENT_CHAR) or line.startswith('//'):
                    self._comments.append(line[1:])
                else:
                    if '=' in line:
                        (part_key, _, part_value) = line.partition('=')
                        if part_value:
                            if len(part_key) == 4:
                                key = int(part_key[:2], 16)
                                subkey = int(part_key[2:], 16)
                                self._dict.setdefault(key, OrderedDict())[subkey] = part_value
                                self._reverse_dict[part_value] = (key, subkey)
                            else:
                                key = int(part_key, 16)
                                if len(part_value) > 1:
                                    self._mte[key] = part_value
                                    self._reverse_mte[part_value] = key
                                else:
                                    self._table[key] = part_value
                                    self._reverse_table[part_value] = key
                    # end of line
                    elif line.startswith(Table.EOL_CHAR):
                        self._eol = int(line[1:len(line)], 16)
                        self._table[int(line[1:len(line)], 16)] = '\n'
            # init reverse
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

    def decode(self, text, tbl_resolver=True, mte_resolver=True, dict_resolver=True, cmd_list=None):
        """ decode bytes into string """
        decoded = []
        if text:
            i = 0
            while i < len(text):
                byte = text[i]
                if True:
                    if cmd_list and byte in cmd_list.keys():
                        decoded.append(self.HEX_FORMAT.format(byte))
                        bytes_to_read = cmd_list.get(byte)
                        for _ in range(bytes_to_read):
                            i += 1
                            byte = text[i]
                            decoded.append(self.HEX_FORMAT.format(byte))
                    elif dict_resolver and byte in self._dict:
                        i += 1
                        byte2 = text[i]
                        if byte2 in self._dict[byte]:
                            decoded.append(self._dict[byte][byte2])
                        else:
                            decoded.append(self.DOUBLE_HEX_FORMAT.format(byte, byte2))
                    elif mte_resolver and byte in self._mte:
                        decoded.append(self._mte[byte])
                    elif tbl_resolver and byte in self._table:
                        decoded.append(self._table[byte])
                    else:
                        decoded.append(self.HEX_FORMAT.format(byte))
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
                        h = self.DOUBLE_HEX_FORMAT.format(key[0], key[1])
                        text = re.sub(r'(?!{})({})(?!{}|.{{1}}{})'.format(self.HEX_FORMAT[0], re.escape(value), self.HEX_FORMAT[-1], self.HEX_FORMAT[-1]), h, text)
            if mte_resolver:
                for value in self._reverse_mte_keys:
                    if value in text:
                        key = self._reverse_mte[value]
                        h = self.HEX_FORMAT.format(key)
                        text = re.sub(r'(?!{})({})(?!{})'.format(self.HEX_FORMAT[0], re.escape(value), self.HEX_FORMAT[-1]), h, text)
            i = 0
            while i < len(text):
                char = text[i]
                if char == self.HEX_FORMAT[0]:
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

    def is_eos(self, key):
        return self._eos == key

    def is_eol(self, key):
        return self._eol == key

    def get_eos(self):
        return self._eos

    def get_eol(self):
        return self._eol

    def get_comments(self):
        return self._comments
