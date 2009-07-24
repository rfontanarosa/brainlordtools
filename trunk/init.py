import os

from PointersTable import PointersTable
from Pointer import Pointer
from HexByteConversion import ByteToHex
from HexByteConversion import HexToByte

import mmap
from brainlord import brainlord_repointer

file = open("Brain Lord (U) [!].smc", "rb+")
size = os.path.getsize("Brain Lord (U) [!].smc")
f = mmap.mmap(file.fileno(), size)


brainlord_repointer(f, "Brain Lord (U) [!] - 2.smc")


f.close()
file.close()