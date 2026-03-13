#v2: Full implementation of FALCOM2 for better compression performance and implement chunking for FALCOM3
import struct
import io
import pdb
from functools import partial

WINDOW_SIZE = 0x1FFF
MIN_MATCH = 2
MAX_MATCH = 0xFF + 0xE
#The real max is 0x7FF0. We have to stop here to make sure to be under.
CHUNK_SIZE_CMP_MAX = 0x7FC0
#The real max is 0x3FFF0. We have to stop here to make sure to be under.
CHUNK_SIZE_UNC_MAX = 0x3DFF0                        
def find_match(filedata, pos):
    if pos < WINDOW_SIZE:                           #Get window to find match in
        window = filedata[:pos]
    else:
        window = filedata[pos - WINDOW_SIZE:pos]
    if pos + MAX_MATCH > len(filedata):             #Avoids EOF errors
        max_match = len(filedata) - pos
    else:
        max_match = MAX_MATCH
    if max_match < MIN_MATCH:                       #Too close to EOF for a match
        return 0, -1
    if filedata[pos:pos + MIN_MATCH] not in window: #No match
        return 0, -1
    for size in range(MIN_MATCH, max_match + 1):    #Look for longest match
        if filedata[pos:pos + size] not in window:
            size -= 1
            break
    match_pos = window.rfind(filedata[pos:pos + size])
    if len(window) - match_pos == size:             #Look for "extra match"
                                                    #For example, find_match(b'abcdabcdabcdabcd', 4)
                                                    #should return match_pos = 4, size = 12
        extra_match = 0; extra_match1 = 0
        multiplier = 0
        while filedata[pos + size + extra_match] == window[match_pos + extra_match1]:
            extra_match += 1; extra_match1 += 1
            if match_pos + extra_match1 == len(window):
                extra_match1 = 0
            if size + extra_match == max_match:
                break
        size += extra_match
    match_pos = len(window) - match_pos              #Convert absolute position to relative
    return size, match_pos
def find_repeat(filedata, pos):
    max_match = 0xFFF + 0xE
    window = filedata[pos:pos + max_match]
    this_byte = filedata[pos]
    repeat_len = 0
    for byte in window:
        if byte == this_byte:
            repeat_len += 1
        else:
            break
    if repeat_len < 0x3:                            #Min match = 0x3
        return 0
    else:
        return repeat_len

def _updateflags(out):
###"Writes" a flag
###Writes data if the flag buffer is full, then flushes
    global comp_buffer
    global flag_pos     #Other functions need read access so it has to be global (or passed back and forth)
    flags = 0
    flag_write = 0x8000
    flag_pos = 8
    b = (yield)         #At this point ready to pass in first flag bit
    while True:
        if b:   #Write a "1" (otherwise write 0)
            flags |= flag_write     #Writes a "1"
        flag_pos -= 1
        if flag_pos == 0:
            out.write(struct.pack('<H', flags))
            out.write(comp_buffer)
            comp_buffer = bytearray(0)
            flag_pos = 16
            flags = 0
        else:
            flags >>= 1
        b = (yield)

def compress_FALCOM3(filedata):
    outdata = io.BytesIO()
    indata = io.BytesIO(filedata)
    #Format is compressed size + 11, decompressed size, chunks, 1st chunk size
    outdata.write(struct.pack('<III',  0, len(filedata), 0))
    first = True
    pos = 0
    i = 0
    while pos < len(filedata):
        i += 1
        if first == True:
            first = False
        else:
            outdata.write(b'\x01')
        data, compressed_len = compress_FALCOM2(filedata[pos:], True)
        pos += compressed_len
        outdata.write(struct.pack('<H', len(data)))
        outdata.write(data)
    outdata.write(b'\x00')                                  #Stop flag
    size = outdata.tell()
    outdata.seek(0)                                         #Write message size
    outdata.write(struct.pack('<I', size - 4))
    outdata.seek(8)                                         #Write number of chunks
    outdata.write(struct.pack('<I', i + 1))
    outdata.seek(0)                                         #Output data
    return outdata.read()

def encode_repeat(repeat_byte, repeat_size, updateflags):
    if repeat_size < 0xE:
        comp_buffer.append(repeat_byte)
        updateflags.send(False)
        encode_match(repeat_size - 1, 1, updateflags)
    else:
        repeat_size -= 0xE
        for x in range(2):
            updateflags.send(True)
        for x in range(4):
            updateflags.send(False)
        comp_buffer.append(1)
        updateflags.send(False)
        if repeat_size < 0x10:
            updateflags.send(False)
            for i in reversed(range(4)):
                updateflags.send((repeat_size >> i) & 1)
                if i == 1:
                    comp_buffer.append(repeat_byte)
        else:
            high_order = repeat_size >> 8
            low_order = repeat_size & 0xFF
            updateflags.send(True)
            for i in reversed(range(4)):
                updateflags.send((high_order >> i) & 1)
                if i == 1:
                    comp_buffer.append(low_order)
                    comp_buffer.append(repeat_byte)
def encode_match(match_size, match_pos, updateflags):    #Encode look-back first (then size)
    if match_pos < 0x100:                   #Short look-back
        updateflags.send(True)          
        comp_buffer.append(match_pos)
        updateflags.send(False)
    else:                                   #Long look-back
        high_order = match_pos >> 8
        low_order = match_pos & 0xFF
        for x in range(2):
            updateflags.send(True)
        for i in reversed(range(5)):
            updateflags.send((high_order >> i) & 1)
            if i == 1:
                comp_buffer.append(low_order)
    for i in range(2, 5):                   #Encode match size
        if i >= match_size:
            break
        updateflags.send(False)
    if match_size >= 6:
        updateflags.send(False)
        if match_size >= 0xE:
            match_size -= 0xE
            comp_buffer.append(match_size)
            updateflags.send(False)
        else:
            updateflags.send(True)
            match_size -= 0x6
            for i in reversed(range(3)):
                updateflags.send((match_size >> i) & 1)
    else:
        updateflags.send(True)
    
def compress_FALCOM2(filedata, FALCOM3 = False):
    global comp_buffer                  #Other functions need write access
    file_size = len(filedata)
    pos = 0
    comp_buffer = bytearray()
    out = io.BytesIO()
    updateflags = _updateflags(out)     #Initalize generator
    next(updateflags)                   #More initialize generator
    while pos < file_size:
        if FALCOM3:
            if out.tell() >= CHUNK_SIZE_CMP_MAX:            #Max compressed data for one chunk (FALCOM3)
                break
            if pos >= CHUNK_SIZE_UNC_MAX:                   #Max uncompressed data for one chunk (FALCOM3)
                break
        match_size, match_pos = find_match(filedata, pos)   #Find matches
        repeat_size = find_repeat(filedata, pos)
        if repeat_size > match_size:                        #Repeat is bigger
            encode_repeat(filedata[pos], repeat_size, updateflags)
            pos += repeat_size
        elif match_size > 0:                                #Match is bigger
            encode_match(match_size, match_pos, updateflags)
            pos += match_size
        else:                                               #No pattern
            comp_buffer.append(filedata[pos])
            pos += 1
            updateflags.send(False)

    for x in range(2):
        updateflags.send(True)
    for x in range(5):
        if x == 4:
            comp_buffer.append(0)
        updateflags.send(False)
    if flag_pos != 0x10:
        for x in range(flag_pos):
            updateflags.send(False)
    out.seek(0)
    if FALCOM3:
        return out.read(), pos
    else:
        return out.read()
if __name__ == '__main__':
    pass
##    with open('mp_0110.cmp', 'wb') as g:
##        with open('mp_0110.orig', 'rb') as f:
##            g.write(compress_FALCOM3(f.read()))