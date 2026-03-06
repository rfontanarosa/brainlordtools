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
        part_label = part_label.replace('\\n', '\n')
        self.value = part_label.strip('\r\n') if part_params == '' else part_label[:part_label.find(']')] + ' '
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
    HEX_CHARS = frozenset('0123456789abcdef')

    def __init__(self, source, encoding='utf-8'):
        self.end_token, self.end_line, self.line_token = None, None, None
        self._table, self._reverse_table = {}, {}
        if isinstance(source, (str, os.PathLike)) and os.path.isfile(source):
            with open(source, 'r', encoding=encoding) as f:
                self._parse(f)
        else:
            with io.StringIO(source) as buffer:
                self._parse(buffer)

    def _parse(self, file_object):
        for line in file_object:
            line = line.strip('\r\n')
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
                        part_value = part_value.replace('\\n', '\n')
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
                if isinstance(node.get(node_key), dict):
                    raise Exception(f"ControlCode key conflicts with existing entry at {node_key!r}")
                node[node_key] = value
            else:
                if isinstance(node.get(node_key), ControlCode):
                    raise Exception(f"Entry key conflicts with existing ControlCode at {node_key!r}")
                new_value = node.setdefault(node_key, {})
                new_value[''] = value
                node[node_key] = new_value
        else:
            existing = node.get(key[0])
            if isinstance(existing, ControlCode):
                raise Exception(f"Entry key prefix conflicts with existing ControlCode at {key[0]!r}")
            self._create_graph(node.setdefault(key[0], {}), key[1:], value)

    def _data_decode(self, node, data, i=1, original_byte=None):
        if original_byte is None:
            original_byte = data[0]
        node = node.get(data[0])
        if isinstance(node, dict) and '' in node:
            if len(data) > 1 and data[1] in node:
                return self._data_decode(node, data[1:], i+1, original_byte)
            else:
                return (i, node[''])
        elif isinstance(node, dict) and len(data) > 1:
            return self._data_decode(node, data[1:], i+1, original_byte)
        elif isinstance(node, ControlCode):
            bytes_to_read = len(node.params)
            if len(data) < bytes_to_read + 1:
                return (1, self.HEX_FORMAT.format(original_byte))
            Bytes = data[1:bytes_to_read + 1]
            return (bytes_to_read + i, node.string_to_format.format(*Bytes))
        else:
            return (1, self.HEX_FORMAT.format(original_byte))

    def _data_encode(self, node, data, i=1, buffer=()):
        node = node.get(data[0])
        if isinstance(node, dict):
            if len(data) > 1 and data[1] in node:
                if '' in node:
                    buffer = (i, node[''])
                return self._data_encode(node, data[1:], i+1, buffer)
            elif '' in node:
                return (i, node[''])
            else:
                if buffer:
                    return (buffer[0], buffer[1])
                return (1, data[0].encode())
        elif isinstance(node, ControlCode):
            if data[0] == ']':
                return (len(node.string_to_format), node.key)
            else:
                Bytes = node.key
                m = re.match(node.re, data[1:])
                if m is None:
                    return (1, data[0].encode())
                for hex_to_decode in m.groups():
                    Bytes += bytes.fromhex(hex_to_decode)
                return (len(node.value) + m.end(), Bytes)
        else:
            char = data[0]
            if char == '{' and len(data) >= 4 and data[3] == '}' and data[1] in self.HEX_CHARS and data[2] in self.HEX_CHARS:
                Byte = bytes.fromhex(data[1:3])
                return (4, Byte)
            else:
                return (1, char.encode())

    def decode(self, data):
        """Transform bytes into a string by traversing the table graph and joining results."""
        if not data:
            return ''
        decoded_parts = []
        i = 0
        data_length = len(data)
        while i < data_length:
            count, value = self._data_decode(self._table, data[i:])
            decoded_parts.append(value)
            i += count
        return "".join(decoded_parts)

    def encode(self, data):
        """Transform a string into bytes by searching the reverse table graph and joining results."""
        if not data:
            return b''
        encoded_parts = []
        i = 0
        data_length = len(data)
        while i < data_length:
            count, value = self._data_encode(self._reverse_table, data[i:])
            encoded_parts.append(value)
            i += count
        return b''.join(encoded_parts)

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
05=[COLOR]
0b00=SWORD
'''
    table = Table(test_table_data)
    test_cases = [
        # end-line token (*fd)
        (b'\xfd', "\n"),
        # end token (/ff)
        (b'\xff', "[END]"),
        # unknown byte fallback to hex format
        (b'\xfe', "{fe}"),
        # 1-byte plain char
        (b'\x01', "A"),
        # 1-byte multi-byte unicode
        (b'\x02', "😆"),
        # 1-byte mapping to 2-char string
        (b'\x03', "aa"),
        # 2-byte entry
        (b'\x04\x00', "bb"),
        # 3-byte entry: longest prefix wins over shorter alternatives (05=[COLOR])
        (b'\x05\x00\x01', "ccc"),
        # 3-byte entry with embedded newline in value
        (b'\x06\x00\x01', "ddd\n"),
        # ControlCode with 1 param byte
        (b'\x07\x00', "[07 00]"),
        # ControlCode with 2 param bytes and trailing newline
        (b'\x08\x00\x01', "[08 00 01]\n"),
        # partial match fallback: \x0b starts 0b00=SWORD but \x05 doesn't complete it
        (b'\x0b\x05', "{0b}[COLOR]"),
        # empty input
        (b'', ""),
        # 1-byte match when longer alternatives exist (05=[COLOR] vs 050001=ccc)
        (b'\x05', "[COLOR]"),
        # 2-byte exact match
        (b'\x0b\x00', "SWORD"),
        # truncated ControlCode: \x07 needs 1 param byte but data ends — fallback to hex (tests bug #4 fix)
        (b'\x07', "{07}"),
        # 2-byte prefix with no match: 0400=bb exists but 0401 does not
        (b'\x04\x01', "{04}A"),
        # multi-entry sequence
        (b'\x01\x02', "A😆"),
        # sequence mixing special tokens
        (b'\xfd\x01\xff', "\nA[END]"),
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
