import struct
import io

outfilename = 'test.cmp'
infilename = 'skill.unc'
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
    out = io.BytesIO()
    data = compress_FALCOM2(filedata)
    #Format is compressed size + 11, decompressed size, chunks, 1st chunk size
    out.write(struct.pack('<IIIH',  len(data) + 11,     #Extra IIHB
                                    len(filedata), 
                                    1, len(data)))
    out.write(data)
    out.write(b'\x00')                                  #Stop flag
    out.seek(0)
    return out.read()

def compress_FALCOM2(filedata):
    global comp_buffer                  #Other functions need write access
    global out
    file_size = len(filedata)
    file_pos = 0
    comp_buffer = bytearray(0)
    out = io.BytesIO()
    updateflags = _updateflags(out) #Initalize generator
    next(updateflags)               #More initialize generator
    while file_pos < file_size:
##        print(hex(file_pos))
        match_size = 0
        match_pos = 0
        if file_pos < 0xFF:
            buffer_start = 0
        else:
            buffer_start = file_pos - 255
        for i, byte in enumerate(filedata[buffer_start:file_pos]):
            i += buffer_start
            if byte == filedata[file_pos]:
                j = 1
                while True:
                    if i + j == file_pos:
                        break
                    if file_pos + j == file_size:
                        break
                    if filedata[i+j] != filedata[file_pos+j]:
                        break
                    j += 1
                if j >= match_size:
                    match_size = j
                    match_pos = file_pos - i
        if match_size > 2:
##            print(match_size)
            if match_size <= 0xFF and match_pos <= 0xFF:
                updateflags.send(True)
                comp_buffer.append(match_pos)
                updateflags.send(False)
                file_pos += match_size
                for i in range(2, 5):
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
            else:
                comp_buffer.append(filedata[file_pos])
                file_pos += 1
                updateflags.send(False)
        else:
            comp_buffer.append(filedata[file_pos])
            file_pos += 1
            updateflags.send(False)
    for x in range(2):
        updateflags.send(True)
    for x in range(5):
        updateflags.send(False)
    for x in range(0x10 - flag_pos):
        updateflags.send(False)
    out.write(b'\x00')
    out.seek(0)
    return out.read()
if __name__ == '__main__':
    pass
    ##with open('skill.unc', 'rb') as f:
    ##    with open('test.cmp', 'wb') as g:
    ##        g.write(compress_FALCOM3(f.read()))