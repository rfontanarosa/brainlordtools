import os
from PointersTable import PointersTable
from Pointer import Pointer
import mmap
from brainlord import *

file = open("Brain Lord (U) [!].smc", "rb+")
size = os.path.getsize("Brain Lord (U) [!].smc")
f = mmap.mmap(file.fileno(), size)


pointers_table = PointersTable(f, TEXT_BLOCK_START)
pointers_table.resolvePointers(f, start=TEXT_BLOCK_START)
pointers_table.toTxt()


f.close()
file.close()

print "puntatori trovati: ", len(pointers_table)


###########################################################################


file = open("Brain Lord (U) [!] - 2.smc", "rb+")
size = os.path.getsize("Brain Lord (U) [!] - 2.smc")
f = mmap.mmap(file.fileno(), size)


pointers_table = PointersTable(f, TEXT_BLOCK_START)
pointers_table.toTxt(filename="pointers_table2.txt")


f.close()
file.close()

print "puntatori trovati: ", len(pointers_table)