__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import re

class ControlCode():

    def __init__(self, hexadecimal_seq, label_and_params):
        self.key = bytes.fromhex(hexadecimal_seq)
        #
        part_label, _, part_params = label_and_params.partition(',')
        self.value = part_label.strip('\r\n').replace('\\n', '\n') if part_params == '' else part_label[:part_label.find(']')] + ' '
        if part_params == '':
            pass
        #
        self.string_to_format = part_label
        if part_params != '':
            self.string_to_format = part_label.replace(']', ' {}]'.format(part_params.replace('%X', '{:02X}').replace(',', ' ')))
        #
        _, _, self.re = part_label.replace(']', ' {}]'.format(part_params.replace('%X', '([a-zA-Z0-9]*)')).replace(',', ' ')).partition(' ')

        self.params = []
        for param in part_params.split(','):
            if param != '':
                param_name, _, param_value = param.partition('=')
                name = param_name if param_value != '' else ''
                value = param_value if param_value != '' else param_name
                self.params.append((name, value))

    def __repr__(self):
        return f'ControlCode - {self.value}'

class Table():

    COMMENT_CHAR = ';'
    END_TOKEN_CHAR = '/'
    END_LINE_CHAR = '*'

    HEX_FORMAT = '{{{:02x}}}'
    DOUBLE_HEX_FORMAT =  HEX_FORMAT + HEX_FORMAT

    def __init__(self, filepath):

        self.end_token, self.end_line = None, None
        self._table, self._reverse_table = {}, {}

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip('\r\n').replace('\\n', '\n')
                if line.startswith(Table.COMMENT_CHAR) or line.startswith('//'):
                    pass
                elif line.startswith(Table.END_TOKEN_CHAR):
                    print(line)
                    self.end_token = bytes.fromhex(line[1:])
                    control_code = ControlCode(line[1:], '[END]\n\n')
                    self._create_graph(self._table, control_code.key, control_code)
                    self._create_graph(self._reverse_table, control_code.value, control_code)
                else:
                    part_key, _, part_value = line.partition('=')
                    if part_value:
                        if len(part_key) % 2 == 0:
                            self._create_graph(self._table, bytes.fromhex(part_key), part_value)
                            self._create_graph(self._reverse_table, part_value, bytes.fromhex(part_key))
                        elif part_key.startswith('$') and len(part_key[1:]) % 2 == 0:
                            control_code = ControlCode(part_key[1:], part_value)
                            self._create_graph(self._table, control_code.key, control_code)
                            self._create_graph(self._reverse_table, control_code.value, control_code)
                        else:
                            raise Exception(line)

    def _create_graph(self, node, key, value):
        print(node)
        print('-----')
        if len(key) == 1:
            node[key if type(key) == str else int.from_bytes(key, byteorder='big')] = value
        else:
            self._create_graph(node.setdefault(key[0], {}), key[1:], value)

    def _data_decode(self, node, data, i=1):
        node = node.get(data[0])
        if type(node) == str:
            return (i, node)
        elif type(node) == dict and len(data) > 1:
            return self._data_decode(node, data[1:], i+1)
        elif type(node) == ControlCode:
            bytes_to_read = len(node.params)
            Bytes = data[1:bytes_to_read + 1]
            return (bytes_to_read + i, node.string_to_format.format(*Bytes))
        else:
            return (1, self.HEX_FORMAT.format(data[0]))

    def _data_encode(self, node, data, i=1):
        node = node.get(data[0])
        if type(node) == bytes:
            return (i, node)
        elif type(node) == dict and len(data) > 1:
            return self._data_encode(node, data[1:], i+1)
        elif type(node) == ControlCode:
            if data[0] == ']':
                return (len(node.string_to_format), node.key)
            else:
                Bytes = node.key
                m = re.match(node.re, data[1:])
                for hex_to_decode in m.groups():
                    Bytes += bytes.fromhex(hex_to_decode)
                return (len(node.value) + m.end(), Bytes)
        else:
            char = data[0]
            if char == self.HEX_FORMAT[0]:
                hex_to_decode = data[i:i+2]
                Byte = bytes.fromhex(hex_to_decode)
                return (4, Byte)
            else:
                return (1, char.encode())

    def decode(self, data):
        """ decode bytes into string """
        decoded = ''
        if data:
            i = 0
            while i < len(data):
                count, value = self._data_decode(self._table, data[i:])
                decoded += value
                i += count
        return decoded

    def encode(self, data):
        """ encode string into bytes """
        encoded = b''
        if data:
            i = 0
            while i < len(data):
                count, value = self._data_encode(self._reverse_table, data[i:])
                encoded += value
                i += count
        return encoded

    def __str__(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(self._reverse_table)
        return self._table.__str__()

if __name__ == "__main__":
    filepath = '/Users/robertofontanarosa/Desktop/table.tbl'
    table = Table(filepath)
    source = b'\xf8\x01\x02\xff\xcc\x04\xff\x05\xff\x99\xfc\x02\x01\xfb\x88\x88\x88\x00\xdd\xff'
    # print(table)
    decoded = table.decode(source)
    print(f'decoded: {decoded}')
    encoded = table.encode(decoded)
    print(f'encoded: {encoded}')
    print(f'encoded hex: {encoded.hex()}')
