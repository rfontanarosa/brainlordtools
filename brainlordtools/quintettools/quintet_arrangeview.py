#
# Quintet Arrangement Viewer
# Osteoclave
# 2011-11-15
#
# This code uses the Pillow fork of the Python Imaging Library (PIL):
# https://pypi.org/project/Pillow/

import sys
import quintet_decomp

from PIL import Image



# Check for incorrect usage.
argc = len(sys.argv)
if argc < 3 or argc > 4:
    print("Usage: {0:s} <inFile> <startOffset> [outFile]".format(sys.argv[0]))
    sys.exit(1)

# Copy the arguments.
inFile = sys.argv[1]
startOffset = int(sys.argv[2], 16)
outFile = "{0:s}_{1:06X}.png".format(inFile, startOffset)
if argc == 4:
    outFile = sys.argv[3]

# Read the input file.
with open(inFile, "rb") as inStream:
    inBytes = inStream.read()

# Read the size bytes.
xSize = 0x10 * inBytes[startOffset + 0]
ySize = 0x10 * inBytes[startOffset + 1]

# Decompress the arrangement data.
outBytes, endOffset = quintet_decomp.decompress(inBytes, startOffset + 2)

# Create the arrangement bitmap.
canvas = Image.new("RGB", (xSize, ySize))

for y in range(ySize):
    for x in range(xSize):

        currentIndex = 0
        currentIndex += (0x10 * xSize * (y // 0x10))
        currentIndex += (0x100 * (x // 0x10))
        currentIndex += (0x10 * (y % 0x10))
        currentIndex += (0x1 * (x % 0x10))

        currentTile = outBytes[currentIndex]

        # This produces a nice orange-and-blue scheme.
        canvas.putpixel(
            (x, y),
            (
                0xFF - abs(currentTile - 0x40),
                0xD0 - abs(currentTile - 0x80),
                0xFF - abs(currentTile - 0xC0)
            )
        )

# Output a scaled-up version of the image, and exit.
canvas.resize((xSize * 4, ySize * 4), Image.NEAREST).save(outFile, "PNG")
sys.exit(0)
