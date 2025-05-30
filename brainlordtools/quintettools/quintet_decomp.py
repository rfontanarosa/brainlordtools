#
# Quintet Decompressor
# Osteoclave
# 2011-07-19
#
# This compression format is used by five of Quintet's games:
#   - ActRaiser
#   - ActRaiser 2
#   - Illusion of Gaia
#   - Robotrek
#   - Soul Blazer
#
# A terse description of the compression format:
#
#    LZSS with a 256-byte sliding window and a 16-byte lookahead,
#    allowing copying of 2-17 previously-seen bytes. The window is
#    initially filled with 0x20s. References to past data use
#    absolute positions in the window and decompressed bytes are
#    written in the window starting at position 0xEF. Control bits
#    (indicating what follows is pastcopy or literal) are part of
#    the stream, rather than being grouped into eights and packed
#    into their own bytes.
#
# In greater detail:
#
#   - Compressed data is prefixed with a 16-bit integer indicating
#     the length of the data once decompressed.
#
#   - Following this is the compressed data itself: a stream of bits
#     that breaks down into two commands, "pastcopy" and "literal".
#     Bits are read from one byte at a time, most significant to
#     least (0x80, 0x40, 0x20 ... 0x01).
#
#        Pastcopy = [0 SSSSSSSS LLLL]
#        Literal  = [1 NNNNNNNN]
#
#   - Pastcopy copies data from the sliding window. The S argument is
#     the source, which is an absolute position in the sliding window
#     (i.e. NOT relative to the last-written position); the L
#     argument indicates how many bytes to copy. Since we'd never
#     copy 0 bytes (wastes 13 bits to do nothing) or 1 byte (using a
#     literal saves 4 bits), we actually copy L+2 bytes.
#
#   - Literal is exactly what it says on the tin. The N argument is
#     one uncompressed byte.
#
#   - Whenever we decompress a byte, we write it to both the output
#     buffer and the sliding window. Curiously, we don't start at the
#     beginning of the window. Instead, the first decompressed byte
#     goes to position 0xEF, the second to position 0xF0, and so on
#     up, wrapping after 0xFF to 0x00.
#
#   - The sliding window is initially populated with 0x20s. One
#     consequence of this is pastcopies from "negative" positions
#     (i.e. copying from sliding window positions that haven't been
#     filled with decompressed bytes yet), which happens if the
#     original data had 0x20s early on.
#
# This code uses python-bitstring:
# https://pypi.org/project/bitstring/

import sys
import bitstring



def decompress(inBytes, startOffset=0):
    # Define some useful constants.
    SEARCH_LOG2 = 8
    SEARCH_SIZE = 2 ** SEARCH_LOG2
    LOOKAHEAD_LOG2 = 4
    LOOKAHEAD_SIZE = 2 ** LOOKAHEAD_LOG2
    BIT_PASTCOPY = 0
    BIT_LITERAL = 1

    # Prepare to read the compressed bytes.
    inStream = bitstring.ConstBitStream(bytes=inBytes)
    inStream.bytepos = startOffset

    # Allocate memory for the decompression process.
    decompSize = inStream.read("uintle:16")
    decomp = bytearray([0x00] * decompSize)
    decompPos = 0
    window = bytearray([0x20] * SEARCH_SIZE)
    windowPos = 0xEF

    # Main decompression loop.
    while decompPos < decompSize:
        nextCommand = inStream.read("uint:1")

        if nextCommand == BIT_PASTCOPY:
            # 0: Pastcopy case.
            copySource = inStream.read(SEARCH_LOG2).uint
            copyLength = inStream.read(LOOKAHEAD_LOG2).uint
            copyLength += 2

            # Truncate copies that would exceed "decompSize" bytes.
            if (decompPos + copyLength) >= decompSize:
                copyLength = decompSize - decompPos

            for i in range(copyLength):
                decomp[decompPos] = window[copySource]
                decompPos += 1
                window[windowPos] = window[copySource]
                windowPos += 1
                windowPos %= SEARCH_SIZE
                copySource += 1
                copySource %= SEARCH_SIZE

        elif nextCommand == BIT_LITERAL:
            # 1: Literal case.
            literalByte = inStream.read("uint:8")
            decomp[decompPos] = literalByte
            decompPos += 1
            window[windowPos] = literalByte
            windowPos += 1
            windowPos %= SEARCH_SIZE

    # Calculate the end offset.
    inStream.bytealign()
    endOffset = inStream.bytepos

    # Return the decompressed data and end offset.
    return (decomp, endOffset)



if __name__ == "__main__":

    # Check for incorrect usage.
    argc = len(sys.argv)
    if argc < 3 or argc > 4:
        print("Usage: {0:s} <inFile> <startOffset> [outFile]".format(
            sys.argv[0]
        ))
        sys.exit(1)

    # Copy the arguments.
    inFile = sys.argv[1]
    startOffset = int(sys.argv[2], 16)
    outFile = None
    if argc == 4:
        outFile = sys.argv[3]

    # Read the input file.
    with open(inFile, "rb") as inStream:
        inBytes = inStream.read()

    # Decompress the data.
    outBytes, endOffset = decompress(inBytes, startOffset)
    outSize = endOffset - startOffset

    # Write the decompressed output, if appropriate.
    if outFile is not None:
        with open(outFile, "wb") as outStream:
            outStream.write(outBytes)

    # Report statistics on the data.
    print("Last offset read, inclusive: {0:X}".format(endOffset - 1))
    print("Compressed size: 0x{0:X} ({0:d}) bytes".format(outSize))
    print("Uncompressed size: 0x{0:X} ({0:d}) bytes".format(len(outBytes)))
    print("Ratio: {0:f}".format(outSize / len(outBytes)))

    # Exit.
    sys.exit(0)
