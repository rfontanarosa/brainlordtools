import argparse
from pathlib import Path

BASE_OFFSET = 0x128400
SPRITE_COUNT = 176
COMPRESSED_SPRITE_SIZE = 0x60
DECOMPRESSED_SPRITE_SIZE = 0x80

# NOTES:
# Sprites 75 and 76 do not exist. They are 192 bytes of 0x00
#
# Sprites with text:
# 9 - EQUIP
# 16/17 - HP
# 62/63 - MP
# 171 - STAT
# 172 - LEVEL
# 173 - ACT.
# 174 - EDIT
# 175 - EDIT


def decompress_icons(comp_data):
    """
    Decompress one or more compressed sprites.
    Input length must be a multiple of 0x60.
    """
    sprite_count = len(comp_data) // COMPRESSED_SPRITE_SIZE
    output = bytearray(sprite_count * DECOMPRESSED_SPRITE_SIZE)

    for i in range(sprite_count):
        base = i * COMPRESSED_SPRITE_SIZE
        comp = bytearray(0x80)
        uncomp = bytearray(0x80)

        # -------------------------------
        # Step 1: expand 3-byte rows → 4-byte grid
        # -------------------------------
        tile = counter = 0
        offset = base

        while counter < 0x80:
            comp[counter] = comp_data[offset]
            comp[counter + 1] = comp_data[offset + 1]
            comp[counter + 0x10] = comp_data[offset + 2]
            comp[counter + 0x11] = 0

            offset += 3
            tile += 2

            if tile == 0x10:
                tile = 0
                counter += 0x10
            counter += 2

        # -------------------------------
        # Step 2: bitplane reconstruction
        # -------------------------------
        tile = counter = 0

        while counter < 0x80:
            for _ in range(8):
                a = 0

                for src in (0x10, 0x01, 0x00):
                    carry = (comp[counter + src] >> 7) & 1
                    comp[counter + src] = (comp[counter + src] << 1) & 0xFF
                    a = ((a << 1) | carry) & 0xFF

                if a == 7:
                    a = 0

                for dst in (0x00, 0x01, 0x10, 0x11):
                    carry = a & 1
                    a >>= 1
                    uncomp[counter + dst] = (
                        (uncomp[counter + dst] << 1) | carry
                    ) & 0xFF

            tile += 2
            if tile == 0x10:
                tile = 0
                counter += 0x10
            counter += 2

        out_base = i * DECOMPRESSED_SPRITE_SIZE
        output[out_base:out_base + DECOMPRESSED_SPRITE_SIZE] = uncomp

    return output


def compress_icons(gfx_data):
    """
    Compress one or all decompressed sprites.
    Input length must be a multiple of 0x80.
    """
    sprite_count = len(gfx_data) // DECOMPRESSED_SPRITE_SIZE
    output = bytearray(sprite_count * COMPRESSED_SPRITE_SIZE)

    for i in range(sprite_count):
        data = bytearray(
            gfx_data[i * DECOMPRESSED_SPRITE_SIZE:(i + 1) * DECOMPRESSED_SPRITE_SIZE]
        )
        comp = bytearray(0x80)

        a = 0
        tile = counter = 0

        # -------------------------------
        # Step 1: rebuild 3BPP values
        # -------------------------------
        while counter < 0x80:
            for _ in range(8):
                for src in (0x11, 0x10, 0x01, 0x00):
                    carry = data[counter + src] & 1
                    data[counter + src] >>= 1
                    a = ((a << 1) | carry) & 0xFF

                if a == 0:
                    a = 7

                for dst in (0x00, 0x01, 0x10):
                    carry = a & 1
                    a >>= 1
                    comp[counter + dst] = ((comp[counter + dst] >> 1) | (carry << 7)) & 0xFF

            tile += 2
            if tile == 0x10:
                tile = 0
                counter += 0x10
            counter += 2

        # -------------------------------
        # Step 2: pack 4-byte rows → 3-byte rows
        # -------------------------------
        tile = counter = 0
        out_offset = i * COMPRESSED_SPRITE_SIZE

        while counter < 0x80:
            output[out_offset] = comp[counter]
            output[out_offset + 1] = comp[counter + 1]
            output[out_offset + 2] = comp[counter + 0x10]

            out_offset += 3
            tile += 2

            if tile == 0x10:
                tile = 0
                counter += 0x10
            counter += 2

    return output


def sprite_region(sprite_index=None):
    """
    Returns (offset, length) for sprite data in ROM.
    If sprite is None, returns the full sprite table region.
    """
    if sprite_index is not None:
        return (
            BASE_OFFSET + sprite_index * COMPRESSED_SPRITE_SIZE,
            COMPRESSED_SPRITE_SIZE,
        )

    length = SPRITE_COUNT * COMPRESSED_SPRITE_SIZE
    return BASE_OFFSET, length


def main():
    parser = argparse.ArgumentParser(description="Secret of Mana Icon Compressor/Extractor")
    sub = parser.add_subparsers(dest="mode", required=True)

    # Extract
    p_ext = sub.add_parser("extract")
    p_ext.add_argument("rom", type=Path)
    p_ext.add_argument("out", type=Path)
    p_ext.add_argument("--sprite", type=int)

    # Insert
    p_ins = sub.add_parser("insert")
    p_ins.add_argument("sprites", type=Path)
    p_ins.add_argument("rom", type=Path)
    p_ins.add_argument("--sprite", type=int)

    args = parser.parse_args()

    if args.mode == "extract":
        rom = args.rom.read_bytes()
        offset, length = sprite_region(args.sprite)

        comp = rom[offset:offset + length]
        data = decompress_icons(comp)

        args.out.write_bytes(data)
        count = len(comp) // COMPRESSED_SPRITE_SIZE
        print(f"Extracted {count} sprite(s)")

    else:
        gfx = args.sprites.read_bytes()
        rom = bytearray(args.rom.read_bytes())
        comp = compress_icons(gfx)

        offset, length = sprite_region(args.sprite)
        rom[offset:offset + length] = comp

        args.rom.write_bytes(rom)
        count = len(comp) // COMPRESSED_SPRITE_SIZE
        print(f"Inserted {count} sprite(s)")


if __name__ == "__main__":
    main()
