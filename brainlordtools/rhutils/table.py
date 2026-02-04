__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import io, os, pprint, re

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

    def __init__(self, source, encoding='utf-8'):
        self.end_token, self.end_line = None, None
        self._table, self._reverse_table = {}, {}
        if isinstance(source, str) and os.path.exists(source):
            with open(source, 'r', encoding=encoding) as f:
                self._parse(f)
        else:
            buffer = io.StringIO(source)
            self._parse(buffer)

    def _parse(self, file_object):
        for line in file_object:
            line = line.strip('\r\n').replace('\\n', '\n')
            if line.startswith(Table.COMMENT_CHAR) or line.startswith('//'):
                pass
            elif line.startswith(Table.END_TOKEN_CHAR):
                self.end_token = bytes.fromhex(line[1:])
                control_code = ControlCode(line[1:], '[END]')
                self._create_graph(self._table, control_code.key, control_code)
                self._create_graph(self._reverse_table, control_code.value, control_code)
            elif line.startswith(Table.END_LINE_CHAR):
                part_key = line[1:]
                self.line_token = bytes.fromhex(part_key)
                self._create_graph(self._table, bytes.fromhex(part_key), '\n')
                self._create_graph(self._reverse_table, '\n', bytes.fromhex(part_key))
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
        if len(key) == 1:
            node_key = key if isinstance(key, str) else int.from_bytes(key, byteorder='big')
            if isinstance(value, ControlCode):
                node[node_key] = value
            else:
                new_value = node.setdefault(node_key, {})
                new_value[''] = value
                node[node_key] = new_value
        else:
            self._create_graph(node.setdefault(key[0], {}), key[1:], value)

    def _data_decode(self, node, data, i=1):
        node = node.get(data[0])
        if isinstance(node, dict) and node.get(''):
            if len(data) > 1 and node.get(data[1]):
                return self._data_decode(node, data[1:], i+1)
            else:
                return (i, node.get(''))
        elif isinstance(node, dict) and len(data) > 1:
            return self._data_decode(node, data[1:], i+1)
        elif isinstance(node, ControlCode):
            bytes_to_read = len(node.params)
            Bytes = data[1:bytes_to_read + 1]
            return (bytes_to_read + i, node.string_to_format.format(*Bytes))
        else:
            return (1, self.HEX_FORMAT.format(data[0]))

    def _data_encode(self, node, data, i=1, buffer=()):
        node = node.get(data[0])
        if isinstance(node, dict):
            if len(data) > 1 and node.get(data[1]):
                if node.get(''):
                    buffer = (i, node.get(''))
                return self._data_encode(node, data[1:], i+1, buffer)
            elif node.get(''):
                return (i, node.get(''))
            else:
                return (buffer[0], buffer[1])
        elif isinstance(node, ControlCode):
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
                hex_to_decode = data[1:3]
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
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(self._reverse_table)
        return self._table.__str__()

if __name__ == "__main__":
    test_table_data = '''
;comment
*fd
/ff
01=A
02=😆
03=aa
0400=bb
050001=ccc
060001=ddd\\n
$07=[07],%X
$08=[08]\\n,%X,%X
'''
    table = Table(test_table_data)
    test_cases = [
        (b'\xfd', "\n"),
        (b'\xff', "[END]"),
        (b'\x01', "A"),
        (b'\x02', "😆"),
        (b'\x03', "aa"),
        (b'\x04\x00', "bb"),
        (b'\x05\x00\x01', "ccc"),
        (b'\x06\x00\x01', "ddd\n"),
        (b'\x07\x00', "[07 00]"),
        (b'\x08\x00\x01', "[08 00 01]\n"),
    ]
    for source_bytes, expected_str in test_cases:
        decoded = table.decode(source_bytes)
        encoded = table.encode(decoded)
        status = "\033[32m" + "PASS" + "\033[0m" if decoded == expected_str and encoded == source_bytes else "\033[31m" + "FAIL" + "\033[0m"
        print(f"Source:  {source_bytes.hex().upper()}")
        print(f"Decoded: {decoded} (Expected: {expected_str})")
        print(f"Encoded: {encoded.hex().upper()}")
        print(f"Result:  {status}")
        print("-" * 40)
