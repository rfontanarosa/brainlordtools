#
# Quintet Compressor
# Osteoclave
# 2012-02-04
#
# The compression format is described in the decompressor.
#
# This code uses python-bitstring:
# https://pypi.org/project/bitstring/

import os
import sys
import bitstring



def compress(inBytes):
    # Define some useful constants.
    SEARCH_LOG2 = 8
    SEARCH_SIZE = 2 ** SEARCH_LOG2
    LOOKAHEAD_LOG2 = 4
    LOOKAHEAD_SIZE = 2 ** LOOKAHEAD_LOG2
    BIT_PASTCOPY = 0
    BIT_LITERAL = 1

    # Prepare the memory buffer.
    inBuffer = bytearray(SEARCH_SIZE + len(inBytes))
    inBuffer[:SEARCH_SIZE] = [0x20] * SEARCH_SIZE
    inBuffer[SEARCH_SIZE:] = inBytes

    # Prepare for compression.
    output = bitstring.BitArray()
    output += bitstring.pack("uintle:16", len(inBytes))
    currentIndex = SEARCH_SIZE

    # Main compression loop.
    while currentIndex < len(inBuffer):
        bestIndex = 0
        bestLength = 0

        # Look for a match in the search buffer. (Brute force)
        for i in range(SEARCH_SIZE):
            # Don't compare past the end of the lookahead buffer.
            # Don't compare past the end of the memory buffer.
            compareLimit = min(
                LOOKAHEAD_SIZE - 1,
                len(inBuffer) - currentIndex
            )

            # Compare the search buffer to the lookahead buffer.
            # Count how many sequential bytes match (possibly zero).
            currentLength = 0
            for j in range(compareLimit):
                if inBuffer[currentIndex - SEARCH_SIZE + i + j] == inBuffer[currentIndex + j]:
                    currentLength += 1
                else:
                    break

            # Keep track of the largest match we've seen.
            if currentLength > bestLength:
                bestIndex = currentIndex - SEARCH_SIZE + i
                bestLength = currentLength

        # Write the next block of compressed output.
        if bestLength >= 2:
            # For some reason, the decompressor expects the pastcopy
            # source values to be offset by 0xEF. I have no idea why.
            bestIndex = (bestIndex + 0xEF) & 0xFF
            output += bitstring.pack("uint:1", BIT_PASTCOPY)
            output += bitstring.pack(
                "uint:n=v", n = SEARCH_LOG2, v = bestIndex
            )
            output += bitstring.pack(
                "uint:n=v", n = LOOKAHEAD_LOG2, v = bestLength - 2
            )
            currentIndex += bestLength
        else:
            output += bitstring.pack("uint:1", BIT_LITERAL)
            output += bitstring.pack("uint:8", inBuffer[currentIndex])
            currentIndex += 1

    # Return the compressed data.
    return output.tobytes()



# Open a file for reading and writing. If the file doesn't exist, create it.
# (Vanilla open() with mode "r+" raises an error if the file doesn't exist.)
def touchopen(filename, *args, **kwargs):
    fd = os.open(filename, os.O_RDWR | os.O_CREAT)
    return os.fdopen(fd, *args, **kwargs)



if __name__ == "__main__":

    # Check for incorrect usage.
    argc = len(sys.argv)
    if argc < 2 or argc > 4:
        print("Usage: {0:s} <inFile> [outFile] [outOffset]".format(
            sys.argv[0]
        ))
        sys.exit(1)

    # Copy the arguments.
    inFile = sys.argv[1]
    outFile = None
    if argc == 3 or argc == 4:
        outFile = sys.argv[2]
    outOffset = 0
    if argc == 4:
        outOffset = int(sys.argv[3], 16)

    # Read the input file.
    with open(inFile, "rb") as inStream:
        inBytes = bytearray(inStream.read())

    # Compress the data.
    outBytes = compress(inBytes)

    # Write the compressed output, if appropriate.
    if outFile is not None:
        with touchopen(outFile, "r+b") as outStream:
            outStream.seek(outOffset)
            outStream.write(outBytes)
            lastOffset = outStream.tell()
            print("Last offset written, inclusive: {0:X}".format(
                lastOffset - 1
            ))

    # Report statistics on the data.
    print("Uncompressed size: 0x{0:X} ({0:d}) bytes".format(len(inBytes)))
    print("Compressed size: 0x{0:X} ({0:d}) bytes".format(len(outBytes)))
    print("Ratio: {0:f}".format(len(outBytes) / len(inBytes)))

    # Exit.
    sys.exit(0)
