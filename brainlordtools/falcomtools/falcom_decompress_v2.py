import io
import pdb
import struct

def decompress_FALCOM3(indata):
    global infilestream, outfilestream          #Other functions need access
    infilestream = io.BytesIO(indata)
    outfilestream = io.BytesIO()
    compressed_size = struct.unpack('<I', infilestream.read(4))[0]
    uncompressed_size = struct.unpack('<I', infilestream.read(4))[0]
    chunks = struct.unpack('<I', infilestream.read(4))[0]
    for x in range(chunks):
        chunk_size = struct.unpack('<H', infilestream.read(2))[0]
        decompress(infilestream, outfilestream)
        if ord(infilestream.read(1)) == 0:
            break
        if outfilestream.tell() >= uncompressed_size:
            break
    outfilestream.seek(0)
    return outfilestream.read()
def decompress_FALCOM2(indata):
    global infilestream, outfilestream          #Other functions need access
    infilestream = io.BytesIO(indata)
    outfilestream = io.BytesIO()
    decompress(infilestream, outfilestream)
    outfilestream.seek(0)
    return outfilestream.read()
def decompress_FALCOM2_1(indata):
    global infilestream, outfilestream          #Other functions need access
    infilestream = io.BytesIO(indata)
    outfilestream = io.BytesIO()
    while True:
        size = struct.unpack('<H', infilestream.read(2))
        decompress(infilestream, outfilestream)
        flag = ord(infilestream.read(1))
        if flag == 0:
            break
    outfilestream.seek(0)
    return outfilestream.read()
def _getflag(f):
    bits = 8    #8 to start off with, then 16
    flags = struct.unpack('<H', f.read(2))[0] >> 8
    while True:
        if bits == 0:
            flags = struct.unpack('<H', f.read(2))[0]
            bits = 16
##            print('load', f.tell())
        flag = flags & 1
##        print(flag, flags)
        flags >>= 1
        bits -= 1
        yield flag
def setup_run(prev_u_buffer_pos):
    global getflag, output
    run = 2
    if not next(getflag):
        run += 1
        if not next(getflag):
            run += 1
            if not next(getflag):
                run += 1
                if not next(getflag):
                    if not next(getflag):
                        run = ord(infilestream.read(1)) + 0xE
                    else:
                        run = 0
                        for x in range(3):
                            run <<= 1
                            run |= next(getflag)
                        run += 0x6
##    print(run, prev_u_buffer_pos, len(output))
#Does the 'copy from buffer' thing
    for x in range(run):
        output.append(output[-1 * prev_u_buffer_pos])
    
def decompress(infilestream, outfilestream):
    global getflag, output              #Other functions need access?
    x = infilestream.tell()
    end_of_stream = infilestream.seek(0, 2)
    infilestream.seek(x)
    output = bytearray(0)
    getflag = _getflag(infilestream)    #Setup/reset generator
    while True:
        if infilestream.tell() == end_of_stream:
            raise Exception('Incomplete compressed stream.')
        if next(getflag):               #Call next method to process next flag
            if next(getflag):           #Long look-back distance or exit program or repeating sequence (flags = 11)
                prev_u_buffer_pos = 0
                run = 0
                for x in range(5):                              #Load high-order distance from flags (max = 0x31)
                    run <<= 1
                    run |= next(getflag)
                prev_u_buffer_pos = ord(infilestream.read(1))   #Load low-order distance (max = 0xFF)
                                                                #Also acts as flag byte
                                                                #run = 0 and byte = 0 -> exit program
                                                                #run = 0 and byte = 1 -> sequence of repeating bytes
                if run != 0:
                    prev_u_buffer_pos |= (run << 8)             #Add high and low order distance (max distance = 0x31FF)
                    setup_run(prev_u_buffer_pos)                #Get run length and finish unpacking (write to output)
                elif prev_u_buffer_pos > 2:                     #Is this used? Seems inefficient.
                    setup_run(prev_u_buffer_pos)
                elif prev_u_buffer_pos == 0:                    #Decompression complete. End program.
##                        pdb.set_trace()
##                        print('hit')
                    break
                else:                                           #Repeating byte
                    branch = next(getflag)                      #True = long repeating sequence (> 30)
                    for x in range(4):                          #Load run length from flags
                        run <<= 1
                        run |= next(getflag)
                    if branch:                                  #Long run length
                        run <<= 0x8                             #Load run length from byte and
                        run |= ord(infilestream.read(1))        #add high-order run length (max = 0xFFF + 0xE)
                    run += 0xE
                    byte = infilestream.read(1)                 #Get byte to repeat
                    for x in range(run):
                        output += byte
            else:                       #Short look-back distance (flags = 10)
                prev_u_buffer_pos = ord(infilestream.read(1))   #Get the look-back distance (max = 0xFF)
                setup_run(prev_u_buffer_pos)                    #Get run length and finish unpacking (write to output)
        else:                           #Copy byte (flags = 0)
            output += infilestream.read(1)                      
    outfilestream.write(output)
if __name__ == '__main__':
    pass
    ##with open('FALCOM2_test.cmp', 'rb') as f:
    ##    with open('output.unc', 'wb') as g:
    ##        g.write(decompress_FALCOM2(f.read()))
    ##with open('skill.tbb', 'rb') as f:
    ##    with open('output.unc', 'wb') as g:
    ##        f.seek(4)
    ##        g.write(decompress_FALCOM3(f.read()))