__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import re
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
        self._controls = OrderedDict()

        self._reverse_table = OrderedDict()
        self._reverse_mte = OrderedDict()
        self._reverse_dict = OrderedDict()
        self._reverse_controls = OrderedDict()

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip('\r\n').replace('\\n', '\n')
                if line.startswith(Table.COMMENT_CHAR) or line.startswith('//'):
                    self._comments.append(line[1:])
                else:
                    if '=' in line:
                        (part_key, _, part_value) = line.partition('=')
                        if part_value:
                            if part_key.startswith('$'):
                                pattern = (part_value + ']').replace(']', '', 1).replace('%X', '{:02x}')
                                if len(part_key) == 5:
                                    key = int(part_key[1:3], 16)
                                    subkey = int(part_key[3:5], 16)
                                    self._controls.setdefault(key, OrderedDict())[subkey] = pattern
                                    self._reverse_controls[part_value] = (key, subkey)
                                elif len(part_key) == 3:
                                    key = int(part_key[1:], 16)
                                    self._controls[key] = pattern
                                    self._reverse_controls[part_value] = key
                                else:
                                    raise Exception()
                            elif len(part_key) == 4:
                                key = int(part_key[:2], 16)
                                subkey = int(part_key[2:], 16)
                                self._dict.setdefault(key, OrderedDict())[subkey] = part_value
                                self._reverse_dict[part_value] = (key, subkey)
                            elif len(part_key) == 2:
                                key = int(part_key, 16)
                                if len(part_value) > 1:
                                    self._mte[key] = part_value
                                    self._reverse_mte[part_value] = key
                                else:
                                    self._table[key] = part_value
                                    self._reverse_table[part_value] = key
                            else:
                                raise Exception()
                    # end of line
                    elif line.startswith(Table.EOL_CHAR):
                        part_key = line[1:]
                        if len(part_key) == 4:
                            key = int(part_key[:2], 16)
                            subkey = int(part_key[2:], 16)
                            self._dict.setdefault(key, OrderedDict())[subkey] = '\n'
                            self._reverse_dict['\n'] = (key, subkey)
                        else:
                            self._eol = int(part_key, 16)
                            self._table[int(part_key, 16)] = '\n'
                            self._reverse_table['\n'] = int(part_key, 16)
            # init reverse
            self._reverse_mte_keys = sorted(self._reverse_mte, key=len, reverse=True)
            self._reverse_dict_keys = sorted(self._reverse_dict, key=len, reverse=True)
            self._reverse_controls_keys = sorted(self._reverse_controls, key=len, reverse=True)

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

    def decode(self, text, tbl_resolver=True, mte_resolver=True, dict_resolver=True, ctrl_resolver=True, cmd_list=None):
        """ decode bytes into string """
        decoded = []
        if text:
            i = 0
            while i < len(text):
                byte = text[i]
                if True:
                    if ctrl_resolver and byte in self._controls.keys():
                        pattern = self._controls[byte]
                        if not isinstance(pattern, str):
                            i += 1
                            byte2 = text[i]
                            pattern = pattern[byte2]
                        count = pattern.count(',')
                        Bytes = text[i+1:i+count+2]
                        decoded.append(pattern.format(*Bytes).replace(',', ' '))
                        i += count
                    elif cmd_list and byte in cmd_list.keys():
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

    def encode(self, text, mte_resolver=True, dict_resolver=True, ctrl_resolver=True):
        """ encode string into bytes """
        encoded = b''
        if text:
            if ctrl_resolver:
                for value in self._reverse_controls_keys:
                    replacements = []
                    key = self._reverse_controls[value]
                    control = value.split(',')[0][1:-1]
                    for m in re.finditer(r'\[{}[^\]]*\]'.format(re.escape(control)), text):
                        replacement = self.HEX_FORMAT.format(key) if not isinstance(key, tuple) else self.DOUBLE_HEX_FORMAT.format(key[0], key[1])
                        text_to_replace = text[m.start():m.end()]
                        for decoded_byte in text_to_replace[:-1].split(' ')[1:]:
                            replacement += self.HEX_FORMAT.format(int(decoded_byte, 16))
                        replacements.append([text_to_replace, replacement])
                    for item in replacements:
                        text = text.replace(item[0], item[1])
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
                    encoded += bytes.fromhex(char_to_decode)
                    i += 3
                else:
                    key = self._reverse_table.get(char)
                    encoded += bytes([key]) if key != None else char.encode()
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
