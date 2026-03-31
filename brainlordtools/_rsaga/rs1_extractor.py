#!/usr/bin/env python3
"""
RS1 Text Extractor
==================
Extracts text blocks from Romancing SaGa (SNES) ROM files.

Based on the RS1Editor Java source by DDSTranslation / Eien Ni Hen.
Reference: rs1source / rs1source-1 (ByteCommands.java, RS1Editor.java)
           /git/brainlordresources/rs1/tools/rs1notes/RS1 notes.txt

Supports four extraction modes:
  - japanese_menu
  - japanese_dialogue
  - english_menu
  - english_dialogue

Usage:
  python3 rs1_extractor.py <rom_file> <mode> [--output <file>]

Example:
  python3 rs1_extractor.py "Romancing SaGa (J) (V1.1) [!].smc" japanese_dialogue
  python3 rs1_extractor.py "Romancing SaGa (U) (V1.2) [!].smc" english_dialogue -o dump.txt
"""

import argparse
import sys


# ============================================================
# ENCODING TABLES
# ============================================================

# English byte → string mapping (from rs1e.tbl + FontTable.java)
# Covers printable characters (0x8A–0xD3) and bigrams (0xD4–0xE5).
ENGLISH_BYTE_TABLE = {
    0x8A: 'A',  0x8B: 'B',  0x8C: 'C',  0x8D: 'D',  0x8E: 'E',  0x8F: 'F',
    0x90: 'G',  0x91: 'H',  0x92: 'I',  0x93: 'J',  0x94: 'K',  0x95: 'L',
    0x96: 'M',  0x97: 'N',  0x98: 'O',  0x99: 'P',  0x9A: 'Q',  0x9B: 'R',
    0x9C: 'S',  0x9D: 'T',  0x9E: 'U',  0x9F: 'V',  0xA0: 'W',  0xA1: 'X',
    0xA2: 'Y',  0xA3: 'Z',
    0xA4: 'a',  0xA5: 'b',  0xA6: 'c',  0xA7: 'd',  0xA8: 'e',  0xA9: 'f',
    0xAA: 'g',  0xAB: 'h',  0xAC: 'i',  0xAD: 'j',  0xAE: 'k',  0xAF: 'l',
    0xB0: 'm',  0xB1: 'n',  0xB2: 'o',  0xB3: 'p',  0xB4: 'q',  0xB5: 'r',
    0xB6: 's',  0xB7: 't',  0xB8: 'u',  0xB9: 'v',  0xBA: 'w',  0xBB: 'x',
    0xBC: 'y',  0xBD: 'z',
    0xBE: '0',  0xBF: '1',  0xC0: '2',  0xC1: '3',  0xC2: '4',  0xC3: '5',
    0xC4: '6',  0xC5: '7',  0xC6: '8',  0xC7: '9',
    0xC8: '.',  0xC9: '!',  0xCA: '?',  0xCB: ',',  0xCC: "'",  0xCD: '"',
    0xCE: ':',  0xCF: '-',  0xD0: '/',  0xD1: ' ',  0xD2: '(',  0xD3: ')',
    # Bigrams / compressed two-character sequences
    0xD4: '[Male]',  0xD5: '[Fem]',
    0xD6: 'la',  0xD7: 'le',  0xD8: 'll',  0xD9: 'ly',  0xDA: 'l ',
    0xDB: 'ie',  0xDC: 'in',  0xDD: 'it',  0xDE: "'s", 0xDF: 'lu',
    0xE0: 'ld',  0xE1: 'd ',  0xE2: 'r ',  0xE3: 'e ',  0xE4: 'y ',  0xE5: 'te',
}


# ============================================================
# ROM REGION CONSTANTS (all file offsets, headerless ROM)
# ============================================================

REGIONS = {
    'japanese_menu': {
        'bank_start':       0x000000,
        'ptr_table_start':  0x007000,
        'ptr_table_end':    0x0070D7,  # inclusive
        'text_end':         0x007E88,
        'bank_read_size':   0x008000,
        'ptr_size':         2,          # bytes per pointer entry
        'language':         'japanese',
        'section':          'menu',
    },
    'japanese_dialogue': {
        'bank_start':       0x0D0000,
        'ptr_table_start':  0x0E2620,
        'ptr_table_end':    0x0E2E1F,  # inclusive
        'text_end':         0x0E261F,
        'bank_read_size':   0x018000,
        'ptr_size':         2,
        'language':         'japanese',
        'section':          'dialogue',
    },
    'english_menu': {
        'bank_start':       0x140000,
        'ptr_table_start':  0x140000,
        'ptr_table_end':    0x1400D7,  # inclusive
        'text_end':         0x141FFF,
        'bank_read_size':   0x008000,
        'ptr_size':         2,
        'language':         'english',
        'section':          'menu',
    },
    'english_dialogue': {
        'bank_start':       0x110000,
        'ptr_table_start':  0x110000,
        'ptr_table_end':    0x110C02,  # inclusive
        'text_end':         0x13FFFF,
        'bank_read_size':   0x030000,
        'ptr_size':         3,          # 24-bit SNES addresses
        'language':         'english',
        'section':          'dialogue',
    },
}


# ============================================================
# TOKEN DECODER (mirrors ByteCommands.bytesToText)
# ============================================================

def decode_token(bank, i, language):
    """
    Decode one token (character or command) from bank starting at index i.
    Returns (text_string, new_i) where new_i points to the byte AFTER
    the last byte consumed (ready for the next call).

    Mirrors the logic in ByteCommands.bytesToText() from the Java source.
    """
    if i >= len(bank):
        return '', i

    b = bank[i]
    i += 1  # advance past the command/char byte

    # ----- Control codes 0x00–0x4C -----

    if b == 0x00:
        arg = bank[i]; i += 1
        return f'<00,{arg:02X}>', i

    elif b == 0x01:
        arg = bank[i]; i += 1
        return f'<01,{arg:02X}>', i

    elif b == 0x02:
        arg = bank[i]; i += 1
        return f'<02,{arg:02X}>', i

    elif b == 0x03:
        arg = bank[i]; i += 1
        return f'<03,{arg:02X}>', i

    elif b == 0x04:
        # Note: decoder reads 1 arg byte (bytesToText), even though the encoder
        # treats <04> as no-argument. Trust the decoder for extraction.
        arg = bank[i]; i += 1
        return f'<04,{arg:02X}>', i

    elif b == 0x05:
        arg = bank[i]; i += 1
        return f'<05,{arg:02X}>', i

    elif b == 0x06:
        arg = bank[i]; i += 1
        return f'<06,{arg:02X}>', i

    elif b == 0x07:
        arg = bank[i]; i += 1
        return f'<07,{arg:02X}>', i

    elif b == 0x08:
        arg = bank[i]; i += 1
        return f'<08,{arg:02X}>', i

    elif b == 0x09:
        arg = bank[i]; i += 1
        return f'<09,{arg:02X}>', i

    elif b == 0x0A:
        return '<0A>', i

    elif b == 0x0B:
        arg = bank[i]; i += 1
        return f'<0B,{arg:02X}>', i

    elif b == 0x0C:
        arg = bank[i]; i += 1
        return f'<0C,{arg:02X}>', i

    elif b == 0x0D:
        arg = bank[i]; i += 1
        return f'<0D,{arg:02X}>', i

    elif b == 0x0E:
        arg = bank[i]; i += 1
        return f'<0E,{arg:02X}>', i

    elif b == 0x0F:  # <movement,XX>
        arg = bank[i]; i += 1
        return f'<movement,{arg:02x}>', i

    elif b == 0x10:  # <newline_window1>
        return '<newline_window1>\n', i

    elif b == 0x11:  # <newline_window2>
        return '<newline_window2>\n', i

    elif b == 0x12:  # <pause>
        return '<pause>', i

    elif b == 0x13:  # <window,XX>
        arg = bank[i]; i += 1
        return f'<window,{arg:02X}>\n', i

    elif b == 0x14:  # <wait,XX>
        arg = bank[i]; i += 1
        return f'<wait,{arg:02x}>', i

    elif b == 0x15:  # <close>
        return '<close>\n', i

    elif b == 0x16:
        return '<16>', i

    elif b == 0x17:  # <selection2>
        return '<selection2>', i

    elif b == 0x18:  # <selection>
        return '<selection>', i

    elif b == 0x19:  # <end_selection2>
        return '<end_selection2>', i

    elif b == 0x1A:
        return '<1A>', i

    elif b == 0x1B:  # <jumpreturn,XXYY>
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<jumpreturn,{lo:02x}{hi:02x}>', i

    elif b == 0x1C:
        return '<1C>', i

    elif b == 0x1D:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<1D,{lo:02x}{hi:02x}>', i

    elif b == 0x1E:
        arg = bank[i]; i += 1
        return f'<1E,{arg:02x}>', i

    elif b == 0x1F:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<1F,{lo:02x}{hi:02x}>', i

    elif b == 0x20:
        arg = bank[i]; i += 1
        return f'<20,{arg:02x}>', i

    elif b == 0x21:  # <text_position,XXYY>
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<text_position,{lo:02x}{hi:02x}>', i

    elif b == 0x22:
        arg = bank[i]; i += 1
        return f'<22,{arg:02x}>', i

    elif b == 0x23:
        return '<23>', i

    elif b == 0x24:
        return '<24>', i

    elif b == 0x25:
        return '<25>', i

    elif b == 0x26:
        return '<26>\n', i

    elif b == 0x27:
        return '<27>\n', i

    elif b == 0x28:  # <checkflag,XXYY>
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<checkflag,{lo:02x}{hi:02x}>', i

    elif b == 0x29:  # <setflag,XXYY>
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<setflag,{lo:02x}{hi:02x}>', i

    elif b == 0x2A:
        arg = bank[i]; i += 1
        return f'<2A,{arg:02x}>', i

    elif b == 0x2B:
        arg = bank[i]; i += 1
        return f'<2B,{arg:02x}>', i

    elif b == 0x2C:  # <name,XX>
        arg = bank[i]; i += 1
        return f'<name,{arg:02x}>', i

    elif b == 0x2D:  # <item,XX>
        arg = bank[i]; i += 1
        return f'<item,{arg:02x}>', i

    elif b == 0x2E:  # <newline_half>
        return '<newline_half>\n', i

    elif b == 0x2F:
        arg = bank[i]; i += 1
        return f'<2F,{arg:02x}>', i

    elif b == 0x30:  # <window_position,XX>
        arg = bank[i]; i += 1
        return f'<window_position,{arg:02x}>', i

    elif b == 0x31:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<31,{lo:02x}{hi:02x}>', i

    elif b == 0x32:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<32,{lo:02x}{hi:02x}>', i

    elif b == 0x33:  # <number,XXYY>
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<number,{lo:02x}{hi:02x}>', i

    elif b == 0x34:
        return '<34>', i

    elif b == 0x35:
        return '<35>\n', i

    elif b == 0x36:
        return '<36>\n', i

    elif b == 0x37:
        return '<37>\n', i

    elif b == 0x38:
        arg = bank[i]; i += 1
        return f'<38,{arg:02x}>', i

    elif b == 0x39:
        arg = bank[i]; i += 1
        return f'<39,{arg:02x}>', i

    elif b == 0x3A:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<3A,{lo:02x}{hi:02x}>', i

    elif b == 0x3B:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<3B,{lo:02x}{hi:02x}>', i

    elif b == 0x3C:
        arg = bank[i]; i += 1
        return f'<3C,{arg:02x}>', i

    elif b == 0x3D:
        # Reads 2 displayed bytes + 1 skipped byte (3 bytes total after command)
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        i += 1  # skip third byte (was used for additional args, now ignored)
        return f'<3D,{lo:02x}{hi:02x}>', i

    elif b == 0x3E:
        return '<3E>\n', i

    elif language == 'japanese' and b == 0x3F:
        # 0x3F = kanji escape prefix; next byte is kanji index
        kanji_idx = bank[i]; i += 1
        return f'[kanji:{kanji_idx:02X}]', i

    elif b == 0x40:
        # Extended multi-sub-command dispatcher
        return _decode_40(bank, i)

    elif b == 0x41:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<41,{lo:02x}{hi:02x}>', i

    elif b == 0x42:
        arg = bank[i]; i += 1
        return f'<42,{arg:02x}>', i

    elif b == 0x43:
        return '<43>\n', i

    elif b == 0x44:
        return '<44>\n', i

    elif b == 0x45:
        return '<45>\n', i

    elif b == 0x46:
        arg = bank[i]; i += 1
        return f'<46,{arg:02x}>', i

    elif b == 0x47:  # <setram,XXYYZZ>
        a = bank[i]; i += 1
        c = bank[i]; i += 1
        d = bank[i]; i += 1
        return f'<setram,{a:02x}{c:02x}{d:02x}>', i

    elif b == 0x48:
        return '<48>\n', i

    elif b == 0x49:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<49,{lo:02x}{hi:02x}>', i

    elif b == 0x4A:
        # Variable-length: 1 byte arg, 1 byte counter, then counter data bytes
        arg = bank[i]; i += 1
        counter = bank[i]; i += 1
        data = ''.join(f'{bank[i + k]:02x}' for k in range(counter))
        i += counter
        return f'<4A,{arg:02x}{counter:02x}{data}>\n', i

    elif b == 0x4B:
        lo = bank[i]; i += 1
        hi = bank[i]; i += 1
        return f'<4B,{lo:02x}{hi:02x}>', i

    elif b == 0x4C:
        return '<4C>\n', i

    elif b == 0xFF:
        return '<FF>\n', i

    # ----- Printable characters -----

    elif language == 'english':
        if b in ENGLISH_BYTE_TABLE:
            return ENGLISH_BYTE_TABLE[b], i
        elif b == 0x3F:
            # Kanji escape in English ROM (mixed Japanese text)
            kanji_idx = bank[i]; i += 1
            return f'[kanji:{kanji_idx:02X}]', i
        else:
            # Unknown byte — output as hex escape
            return f'[{b:02X}]', i

    elif language == 'japanese':
        if 0x4D <= b <= 0xFF:
            # Japanese kana/symbol byte — output as hex escape
            # (Actual kana mapping requires FontTable.japaneseByteTable,
            #  which uses Shift-JIS encoded characters not included here)
            return f'[jp:{b:02X}]', i
        else:
            print(f'  [WARNING] Unknown byte 0x{b:02X} at index {i - 1}', file=sys.stderr)
            return f'[{b:02X}]', i

    else:
        print(f'  [WARNING] Unhandled byte 0x{b:02X} at index {i - 1}', file=sys.stderr)
        return f'[{b:02X}]', i


def _decode_40(bank, i):
    """
    Handle the 0x40 extended command dispatcher.
    i points to the sub-command byte (byte AFTER the 0x40 command byte).
    Returns (text, new_i).
    """
    sub = bank[i]; i += 1

    # Sub-commands with no extra bytes
    no_arg_subs = {
        0x00, 0x01, 0x02, 0x03, 0x05, 0x0E, 0x0F, 0x13, 0x15,
        0x18, 0x1A, 0x1C, 0x1D, 0x23, 0x24, 0x26, 0x27, 0x28,
        0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x35, 0x37,
        0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40,
        0x43, 0x44, 0x45, 0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x4F,
        0x50, 0x51, 0x52, 0x54, 0x55, 0x56, 0x59, 0x5D, 0x5E,
        0x5F, 0x60, 0x61, 0x62, 0x64, 0x65, 0x66, 0x67, 0x6A,
        0x6B, 0x6D, 0x6E, 0x6F, 0x70, 0x71, 0x72, 0x74, 0x75,
        0x79, 0x93, 0xE1, 0xEE,
    }
    # Sub-commands with 1 extra byte
    one_arg_subs = {
        0x11, 0x12, 0x17, 0x19, 0x1B, 0x1F, 0x21, 0x25,
        0x36, 0x42, 0x46, 0x47, 0x4D, 0x4E, 0x57, 0x63,
        0x69, 0x6C, 0x73, 0x77, 0x78, 0xE9,
    }
    # Sub-commands with 2 extra bytes
    two_arg_subs = {
        0x1E, 0x29, 0x31, 0x33, 0x34, 0x58, 0x5B, 0x5C, 0x9E,
    }
    # Sub-commands with 3 extra bytes
    three_arg_subs = {0x68}

    if sub in no_arg_subs:
        return f'<40,{sub:02X}>', i

    elif sub in one_arg_subs:
        arg = bank[i]; i += 1
        return f'<40,{sub:02X}{arg:02X}>', i

    elif sub in two_arg_subs:
        a = bank[i]; i += 1
        b2 = bank[i]; i += 1
        return f'<40,{sub:02X}{a:02X}{b2:02X}>', i

    elif sub in three_arg_subs:
        a = bank[i]; i += 1
        b2 = bank[i]; i += 1
        c = bank[i]; i += 1
        return f'<40,{sub:02X}{a:02X}{b2:02X}{c:02X}>', i

    else:
        print(f'  [WARNING] Unknown 0x40 sub-command: 0x{sub:02X}', file=sys.stderr)
        return f'<40,{sub:02X}>', i


# ============================================================
# BLOCK DECODER
# ============================================================

def decode_block(bank, start, stop, language):
    """
    Decode all tokens in the bank from index `start` up to and including
    `stop`. Mirrors populateBlock() from RS1Editor.java.

    Returns the decoded text string.
    """
    i = start
    parts = []

    while i <= stop:
        if i >= len(bank):
            break
        text, i = decode_token(bank, i, language)
        parts.append(text)

        # Stop at end-of-block marker if stop is unknown (== 0)
        if stop == 0 and text.startswith('<FF>'):
            break

    return ''.join(parts)


# ============================================================
# SNES ADDRESS → BANK ARRAY OFFSET (English Dialogue)
# ============================================================

def snes_to_bank_offset(snes_addr):
    """
    Convert a 24-bit SNES address (from the English Dialogue pointer table)
    to a flat index into the loaded bank array.

    The English Dialogue bank is loaded from file offset 0x110000, which
    corresponds to SNES $22:8000. Each SNES bank in LoROM is 0x8000 bytes.

    Mapping:
      SNES $22:8000–$22:FFFF → bank[0x00000–0x07FFF]
      SNES $23:8000–$23:FFFF → bank[0x08000–0x0FFFF]
      SNES $24:8000–$24:FFFF → bank[0x10000–0x17FFF]
      SNES $25:8000–$25:FFFF → bank[0x18000–0x1FFFF]
      SNES $26:8000–$26:FFFF → bank[0x20000–0x27FFF]
      SNES $27:8000–$27:FFFF → bank[0x28000–0x2FFFF]
    """
    if snes_addr < 0x238000:
        return snes_addr - 0x228000
    elif snes_addr < 0x248000:
        return snes_addr - 0x230000
    elif snes_addr < 0x258000:
        return snes_addr - 0x238000
    elif snes_addr < 0x268000:
        return snes_addr - 0x240000
    else:
        return snes_addr - 0x248000


# ============================================================
# POINTER TABLE READER
# ============================================================

def read_pointers(bank, region):
    """
    Read all pointer values from the pointer table embedded in `bank`.
    Returns a list of (pointer_address_in_bank, pointer_value) tuples.
    """
    language = region['language']
    section = region['section']
    bank_start = region['bank_start']
    ptr_table_start = region['ptr_table_start']
    ptr_table_end = region['ptr_table_end']
    ptr_size = region['ptr_size']

    pointers = []

    if language == 'english' and section == 'dialogue':
        # 3-byte (24-bit SNES address) pointers
        ptr_count = (ptr_table_end - ptr_table_start - 2) // 3
        for i in range(ptr_count):
            offset = i * 3
            addr_in_bank = (ptr_table_start - bank_start) + offset
            lo  = bank[addr_in_bank]
            mid = bank[addr_in_bank + 1]
            hi  = bank[addr_in_bank + 2]
            value = lo + 0x100 * mid + 0x10000 * hi
            pointers.append((addr_in_bank, value))
    else:
        # 2-byte pointers
        ptr_count = (ptr_table_end - ptr_table_start + 1) // 2
        for i in range(ptr_count):
            offset = i * 2
            addr_in_bank = (ptr_table_start - bank_start) + offset
            lo = bank[addr_in_bank]
            hi = bank[addr_in_bank + 1]

            if section == 'dialogue':
                # Japanese dialogue: pointer values wrap at offset 0x6D4 in
                # the pointer table (the text crosses a 64KB boundary).
                if offset >= 0x6D4:
                    value = 0x10000 + lo + 256 * hi
                else:
                    value = lo + 256 * hi
            elif section == 'menu':
                if language == 'japanese':
                    # Japanese menu: add 0x7100 to convert to bank array index.
                    value = lo + 256 * hi + 0x7100
                else:
                    # English menu: values are already bank array indices.
                    value = lo + 256 * hi
            else:
                value = lo + 256 * hi

            pointers.append((addr_in_bank, value))

    return pointers


# ============================================================
# MAIN EXTRACTOR
# ============================================================

def extract(rom_path, mode, output_path=None):
    if mode not in REGIONS:
        print(f'Error: unknown mode "{mode}". Choose from: {list(REGIONS.keys())}',
              file=sys.stderr)
        sys.exit(1)

    region = REGIONS[mode]
    language = region['language']
    section  = region['section']
    bank_start = region['bank_start']
    bank_read_size = region['bank_read_size']

    # --- Load bank from ROM ---
    print(f'Loading ROM: {rom_path}')
    try:
        with open(rom_path, 'rb') as f:
            f.seek(bank_start)
            bank = bytearray(f.read(bank_read_size))
    except FileNotFoundError:
        print(f'Error: ROM file not found: {rom_path}', file=sys.stderr)
        sys.exit(1)

    print(f'Mode: {mode}  |  Language: {language}  |  Section: {section}')
    print(f'Bank loaded: 0x{bank_start:06X} – 0x{bank_start + bank_read_size - 1:06X} '
          f'({bank_read_size} bytes)')

    # --- Read pointer table ---
    pointers = read_pointers(bank, region)
    print(f'Pointer count: {len(pointers)}')

    # --- Resolve start/stop offsets for each block ---
    blocks = []
    if language == 'english' and section == 'dialogue':
        # Pointer values are 24-bit SNES addresses; convert to bank array offsets.
        for idx, (ptr_addr, snes_value) in enumerate(pointers):
            start = snes_to_bank_offset(snes_value)
            if idx < len(pointers) - 1:
                stop = snes_to_bank_offset(pointers[idx + 1][1]) - 1
            else:
                stop = start + 1  # last block: minimal safe stop
            blocks.append((idx, ptr_addr, snes_value, start, stop))
    else:
        # Pointer values are direct bank array indices.
        for idx, (ptr_addr, value) in enumerate(pointers):
            start = value
            if idx < len(pointers) - 1:
                stop = pointers[idx + 1][1] - 1
            else:
                stop = 0  # 0 = "read until <FF>" sentinel
            blocks.append((idx, ptr_addr, value, start, stop))

    # --- Decode and output ---
    lines = []
    for block_id, ptr_addr, ptr_value, start, stop in blocks:
        # Guard against out-of-range starts
        if start >= len(bank) or start < 0:
            print(f'  [WARNING] Block {block_id}: start 0x{start:X} out of range '
                  f'(bank size 0x{len(bank):X})', file=sys.stderr)
            continue

        text = decode_block(bank, start, stop, language)

        lines.append('>>>>>>>>>>')
        lines.append(f'Block {block_id}:')
        lines.append(text)

    output = '\n'.join(lines)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Output written to: {output_path}')
    else:
        print(output)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='RS1 Text Extractor — Romancing SaGa (SNES)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''\
Modes:
  japanese_menu       Menu/status text from the Japanese ROM
  japanese_dialogue   Dialogue text from the Japanese ROM
  english_menu        Menu/status text from the English fan-translation ROM
  english_dialogue    Dialogue text from the English fan-translation ROM

Examples:
  python3 rs1_extractor.py "Romancing SaGa (J) (V1.1) [!].smc" japanese_dialogue
  python3 rs1_extractor.py "Romancing SaGa (U) (V1.2) [!].smc" english_dialogue -o dump.txt
''')
    parser.add_argument('rom', help='Path to the ROM file (headerless .smc)')
    parser.add_argument('mode', choices=list(REGIONS.keys()), help='Extraction mode')
    parser.add_argument('-o', '--output', default=None, help='Output file (default: stdout)')
    args = parser.parse_args()

    extract(args.rom, args.mode, args.output)


if __name__ == '__main__':
    main()
