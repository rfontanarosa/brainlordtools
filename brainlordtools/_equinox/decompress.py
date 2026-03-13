#!/usr/bin/env python3
"""
Equinox (SNES) graphics decompressor.

Reverse-engineered from the decompression dispatch at $89:F38E.
Supports two modes used by the title screen loader at $88:86FD:

  Mode $0004 ($89:F52B) - Tile compression:
    - 3 priority fill masks ($00, $FF, shared byte) with bitfields
    - 2-color bitplane encoding (1bpp + 4-bit color -> 4bpp interleaved)
    - Recursive sub-blocks with offset references
    - Post-processing: bit transpose (flag bit 7), byte-pair reversal (bit 0),
      lookup table substitution (bit 1 in sub-block context)
    - Overlay of specific bytes after sub-block return (bit 5 in sub-block context)

  Mode $0006 ($89:F964) - Raw copy:
    - Straight byte-for-byte copy, no compression.

Output: SNES 4bpp interleaved tile data (16 bytes per bitplane pair per tile row).
"""

import sys
import os

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class EquinoxDecompressor:
    def __init__(self, rom_data, start_offset, size):
        """
        rom_data: full ROM bytes
        start_offset: ROM file offset of compressed data start
        size: compressed data size in bytes
        """
        self.rom = rom_data
        self.base = start_offset
        self.pos = start_offset
        self.end = start_offset + size
        self.output = bytearray()
        self.buffer = bytearray(32)
        self.stack = []
        # LUT for sub-block bit 1 substitution: bit-reversal table at ROM $02CBF
        self.sub_table = bytes(rom_data[0x02CBF + i] for i in range(256))

    def read_byte(self):
        if self.pos >= len(self.rom):
            raise ValueError(f"Read past ROM end at offset ${self.pos:X}")
        b = self.rom[self.pos]
        self.pos += 1
        return b

    def decompress(self):
        """Main decompression loop (mode $0004, $89:F52B)."""
        while self.pos < self.end:
            self._process_block()
        return bytes(self.output)

    def raw_copy(self):
        """Raw copy mode (mode $0006, $89:F964)."""
        size = self.end - self.pos
        self.output = bytearray(self.rom[self.pos:self.pos + size])
        self.pos += size
        return bytes(self.output)

    def _process_block(self):
        flags = self.read_byte()

        if flags & 0x40:
            self._decode_bitplane_block(flags)
        elif flags & 0x30:
            self._decode_subblock_ref(flags)
            return
        else:
            self._decode_direct_tile(flags)

        if flags & 0x80:
            self._bit_transpose()

        self._handle_stack_return()

    def _decode_bitplane_block(self, flags):
        combined_mask = 0

        if flags & 0x20:
            mask = self.read_byte()
            combined_mask |= mask
            for i in range(8):
                if mask & (1 << i):
                    self.buffer[i] = 0x00

        if flags & 0x10:
            mask = self.read_byte()
            combined_mask |= mask
            for i in range(8):
                if mask & (1 << i):
                    self.buffer[i] = 0xFF

        for i in range(8):
            if not (combined_mask & (1 << i)):
                self.buffer[i] = self.read_byte()

        color0_bp0 = 0x80 if (flags & 0x01) else 0x00
        color0_bp1 = 0x80 if (flags & 0x02) else 0x00
        color1_bp0 = 0x80 if (flags & 0x04) else 0x00
        color1_bp1 = 0x80 if (flags & 0x08) else 0x00

        for byte_idx in range(7, -1, -1):
            pixel_byte = self.buffer[byte_idx]
            result = 0

            for bit in range(8):
                result >>= 1
                if pixel_byte & 1:
                    result |= (color1_bp1 << 8) | color1_bp0
                else:
                    result |= (color0_bp1 << 8) | color0_bp0
                pixel_byte >>= 1

            self.buffer[byte_idx * 2] = result & 0xFF
            self.buffer[byte_idx * 2 + 1] = (result >> 8) & 0xFF

    def _decode_direct_tile(self, flags):
        mask_00 = 0
        mask_ff = 0
        mask_shared = 0
        shared_byte = 0

        if flags & 0x04:
            lo = self.read_byte()
            hi = self.read_byte()
            mask_00 = lo | (hi << 8)

        if flags & 0x02:
            lo = self.read_byte()
            hi = self.read_byte()
            mask_ff = lo | (hi << 8)

        if flags & 0x01:
            shared_byte = self.read_byte()
            lo = self.read_byte()
            hi = self.read_byte()
            mask_shared = lo | (hi << 8)

        for i in range(16):
            bit = 1 << i
            if mask_00 & bit:
                self.buffer[i] = 0x00
            elif mask_ff & bit:
                self.buffer[i] = 0xFF
            elif mask_shared & bit:
                self.buffer[i] = shared_byte
            else:
                self.buffer[i] = self.read_byte()

    def _decode_subblock_ref(self, flags):
        offset_lo = self.read_byte()
        offset_hi = self.read_byte()
        offset = offset_lo | (offset_hi << 8)

        self.stack.append((flags, self.pos))
        self.pos = self.base + offset

    def _handle_stack_return(self):
        if not self.stack:
            self.output.extend(self.buffer[:16])
            return

        parent_flags, return_pos = self.stack.pop()
        self.pos = return_pos

        if parent_flags & 0x20:
            mask_lo = self.read_byte()
            mask_hi = self.read_byte()
            mask = mask_lo | (mask_hi << 8)
            for i in range(16):
                if mask & (1 << i):
                    self.buffer[i] = self.read_byte()

        if parent_flags & 0x01:
            for i in range(0, 8, 2):
                j = 14 - i
                self.buffer[i], self.buffer[j] = self.buffer[j], self.buffer[i]
                self.buffer[i+1], self.buffer[j+1] = self.buffer[j+1], self.buffer[i+1]

        if parent_flags & 0x02:
            if self.sub_table is not None:
                for i in range(16):
                    self.buffer[i] = self.sub_table[self.buffer[i]]

        if parent_flags & 0x80:
            self._bit_transpose()

        self._handle_stack_return()

    def _bit_transpose(self):
        out = bytearray(16)
        byte_idx = 0
        bit_mask = 0x80

        for _ in range(8):
            bp0 = self.buffer[byte_idx]
            bp1 = self.buffer[byte_idx + 1]
            byte_idx += 2

            for row in range(7, -1, -1):
                if bp0 & 0x80:
                    out[row * 2] |= bit_mask
                bp0 = (bp0 << 1) & 0xFF
                if bp1 & 0x80:
                    out[row * 2 + 1] |= bit_mask
                bp1 = (bp1 << 1) & 0xFF

            bit_mask >>= 1

        self.buffer[:16] = out


def snes_4bpp_to_pixels(tile_data):
    """Convert 32 bytes of SNES 4bpp tile to 8x8 pixel array (0-15)."""
    pixels = []
    for row in range(8):
        bp01 = row * 2
        bp23 = 16 + row * 2
        bp0 = tile_data[bp01] if bp01 < len(tile_data) else 0
        bp1 = tile_data[bp01 + 1] if bp01 + 1 < len(tile_data) else 0
        bp2 = tile_data[bp23] if bp23 < len(tile_data) else 0
        bp3 = tile_data[bp23 + 1] if bp23 + 1 < len(tile_data) else 0
        row_pixels = []
        for bit in range(7, -1, -1):
            p = 0
            if bp0 & (1 << bit): p |= 1
            if bp1 & (1 << bit): p |= 2
            if bp2 & (1 << bit): p |= 4
            if bp3 & (1 << bit): p |= 8
            row_pixels.append(p)
        pixels.append(row_pixels)
    return pixels


def save_tiles_png(data, out_path, tiles_per_row=16):
    """Save 4bpp tile data as a grayscale PNG."""
    if not HAS_PIL:
        print(f"  (Skipping PNG: install Pillow for image output)")
        return
    num_tiles = len(data) // 32
    if num_tiles == 0:
        return
    num_rows = (num_tiles + tiles_per_row - 1) // tiles_per_row
    img = Image.new("L", (tiles_per_row * 8, num_rows * 8), 0)
    palette = [int(i * 255 / 15) for i in range(16)]

    for idx in range(num_tiles):
        tile = data[idx * 32:(idx + 1) * 32]
        pixels = snes_4bpp_to_pixels(tile)
        tx = (idx % tiles_per_row) * 8
        ty = (idx // tiles_per_row) * 8
        for r in range(8):
            for c in range(8):
                img.putpixel((tx + c, ty + r), palette[pixels[r][c]])

    img.save(out_path)
    print(f"  Saved PNG: {out_path}")


def main():
    rom_path = "Z:/Romhacking/Equinox SNES/rom/Equinox (U).sfc"

    with open(rom_path, "rb") as f:
        rom = f.read()

    # =========================================================================
    # Data set 1: Compressed tiles (1st JSL $89:F38E call at $88:86FD)
    #   Parameters: A=$0200, X=$6000, Y=$002A
    #   Mode $0004 -> decompressor at $89:F52B
    #   Source: SNES $0E:B169, ROM $73169
    #   Size: $23BA (9146 bytes, from size table at $00:F95F+$2A)
    #   VRAM dest: $6000
    # =========================================================================
    print("=== Data set 1: Compressed tiles ===")
    ds1_start = 0x73169
    ds1_size = 0x23BA
    print(f"  Source: ROM ${ds1_start:05X}, size ${ds1_size:04X} ({ds1_size} bytes)")

    decomp1 = EquinoxDecompressor(rom, ds1_start, ds1_size)
    try:
        result1 = decomp1.decompress()
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Position: ROM ${decomp1.pos:05X}")
        print(f"  Output so far: {len(decomp1.output)} bytes")
        result1 = bytes(decomp1.output)

    print(f"  Decompressed: {len(result1)} bytes ({len(result1)//32} 4bpp tiles)")

    with open("Z:/Romhacking/Equinox SNES/decompressed_set1.bin", "wb") as f:
        f.write(result1)
    print(f"  Saved: decompressed_set1.bin")
    save_tiles_png(result1, "Z:/Romhacking/Equinox SNES/decompressed_set1.png")

    # =========================================================================
    # Data set 2: Raw (uncompressed) tiles (2nd JSL $89:F38E call)
    #   Parameters: A=$007F, X=$8000, Y=$001A
    #   Mode $0006 -> raw copy at $89:F964
    #   Source: SNES $0D:EFE9, ROM $6EFE9
    #   Size: $2000 (8192 bytes = 256 tiles, from size table at $00:F95F+$1A)
    #   VRAM dest: $8000
    # =========================================================================
    print()
    print("=== Data set 2: Raw (uncompressed) tiles ===")
    ds2_start = 0x6EFE9
    ds2_size = 0x2000
    print(f"  Source: ROM ${ds2_start:05X}, size ${ds2_size:04X} ({ds2_size} bytes)")

    decomp2 = EquinoxDecompressor(rom, ds2_start, ds2_size)
    result2 = decomp2.raw_copy()

    print(f"  Copied: {len(result2)} bytes ({len(result2)//32} 4bpp tiles)")

    with open("Z:/Romhacking/Equinox SNES/decompressed_set2.bin", "wb") as f:
        f.write(result2)
    print(f"  Saved: decompressed_set2.bin")
    save_tiles_png(result2, "Z:/Romhacking/Equinox SNES/decompressed_set2.png")

    # =========================================================================
    # Data set 3: Compressed tiles (JSL $89:F38E call at $88:85F6)
    #   Parameters: A=$0200, X=$5000, Y=$002C
    #   Mode $0004 -> decompressor at $89:F52B
    #   Source: SNES $0E:D523, ROM $75523
    #   Size: $0552 (1362 bytes, from size table at $00:F95F+$2C)
    #   VRAM dest: $5000
    # =========================================================================
    print()
    print("=== Data set 3: Compressed tiles ===")
    ds3_start = 0x75523
    ds3_size = 0x0552
    print(f"  Source: ROM ${ds3_start:05X}, size ${ds3_size:04X} ({ds3_size} bytes)")

    decomp3 = EquinoxDecompressor(rom, ds3_start, ds3_size)
    try:
        result3 = decomp3.decompress()
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Position: ROM ${decomp3.pos:05X}")
        print(f"  Output so far: {len(decomp3.output)} bytes")
        result3 = bytes(decomp3.output)

    print(f"  Decompressed: {len(result3)} bytes ({len(result3)//32} 4bpp tiles)")

    with open("Z:/Romhacking/Equinox SNES/decompressed_set3.bin", "wb") as f:
        f.write(result3)
    print(f"  Saved: decompressed_set3.bin")
    save_tiles_png(result3, "Z:/Romhacking/Equinox SNES/decompressed_set3.png")

    # =========================================================================
    # Combined output
    # =========================================================================
    print()
    combined = result1 + result2 + result3
    with open("Z:/Romhacking/Equinox SNES/decompressed_combined.bin", "wb") as f:
        f.write(combined)
    print(f"=== Combined: {len(combined)} bytes ({len(combined)//32} tiles total) ===")
    print(f"  Saved: decompressed_combined.bin")
    save_tiles_png(combined, "Z:/Romhacking/Equinox SNES/decompressed_combined.png")


if __name__ == "__main__":
    main()
