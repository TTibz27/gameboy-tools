import argparse
import numpy as np
import mmap


def main():
    # global variables
    global uniqueCommands
    global commandMap
    global operandMap
    uniqueCommands = []
    commandMap = []
    operandMap = []

    # read arguments
    parser = argparse.ArgumentParser(description='Convert VGM file to assembly.')
    parser.add_argument('infile', help='input VGM file')
    parser.add_argument('outfile', help='output ASM file')
    args = parser.parse_args()

    # read from file
    headerSize = 256
    headerNumpy = np.fromfile(args.infile, dtype=np.uint8, count=headerSize, sep='', offset=0)

    # handle header info
    fileSignature = headerNumpy[0:4].view('S4').squeeze()
    print(chr(headerNumpy[0]))
    print(str(fileSignature, "utf-8"))
    if str(fileSignature, "utf-8") != "Vgm ":
        print("Invalid header, file identification was incorrect")
        exit  # SHOULD BE RETURN EVENTUALLY, this should be a function likely

    # end of file offset shouldnt actually matter?
    eofOffset = (headerNumpy[4:8].view('<i4')) + 0x04  # <i4 = little endian uint32
    print(eofOffset)

    # this tells us where the start of the metadata at the end of file is, this should be the effective end of file
    gd3MetadataOffset = (headerNumpy[0x14:0x18].view('<i4')) + 0x14  # 0x14 - 0x18
    print(gd3MetadataOffset)

    # 0x18 - 0x23 are about loops, important for playback but not for converting to raw ASM read/writes.

    gbHertz = headerNumpy[0x80:0x84].view('<i4')  # 0x80 - 0x83
    print(gbHertz)
    if gbHertz < 1000:
        print("VGM file does not appear to be in a gameboy format, aborting.")
        exit()

    dataStart = headerNumpy[0x34:0x38].view('<i4') + 0x34
    print(dataStart)

    dataSizeBytes = gd3MetadataOffset[0] - dataStart[0]
    print(dataSizeBytes)
    bodyNumpy = np.fromfile(args.infile, dtype=np.uint8, count=-1, sep='', offset=dataStart[0])

    # for x in headerNumpy:
    # print (hex(x))

    # print (hex(bodyNumpy[0]))
    # Read file and reshape as "records" of 28 bytes each
    # n = np.fromfile('fort.99',dtype=np.uint8).reshape(-1,28)
    # I = n[:,4:8].copy().view(np.int32)     # pick bytes 4-8, make contiguous and view as integer
    # A = n[:,8:16].copy().view(np.float64)  # pick bytes 8-16, make contiguous and view as float64
    # B = n[:,16:24].copy().view(np.float64) # p

    with open(args.infile, 'rb', 0) as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as filemap:
        filemap = filemap[dataStart[0]:gd3MetadataOffset[0]]
        testvar = 0
        commandOperandsRemaining = 0

        commandType = ''

        commandOperandsArray = []
        global waitFrames
        waitFrames = 0
        for byte in filemap:  # length is equal to the current file size
            # is this byte an operand for a previous command?
            if commandOperandsRemaining > 0:
                # if commandType == 'LOAD_TO_REGISTER':
                commandOperandsArray.append(byte)
                commandOperandsRemaining -= 1

            # else we load a command

            # This is essentially a LD command
            elif byte == 0xb3:
                commandOperandsRemaining = 2
                commandType = 'LOAD_TO_REGISTER'

            elif byte == 0x62:
                commandOperandsRemaining = 0
                commandType = 'WAIT_60TH'

            elif byte == 0x61:
                commandOperandsRemaining = 2
                commandType = 'WAIT_LONG'

            elif byte == 0x66:
                commandOperandsRemaining = 0
                commandType = 'END_OF_SONG'

            else:
                print("unknown command found: {0}".format(hex(byte)))

            # Process a completed command
            if commandOperandsRemaining == 0 and commandType != '':
                process_command(commandType, commandOperandsArray)

                commandType = ''
                commandOperandsArray = []
    print("finished parsing!")

    print ("saving....")
    with open(args.outfile+ ".cmd.bin", "wb") as outfile:
        for i in commandMap:
            outfile.write(i.to_bytes(1, 'little'))

    with open(args.outfile + ".val.bin", "wb") as outfile:
        for i in operandMap:
            outfile.write(i.to_bytes(1, 'little'))

    print(commandMap)
    print(len(commandMap))
    print(operandMap)
    print(len(operandMap))


def process_command(command_type, command_operands):
    global waitFrames
    global uniqueCommands
    global commandMap
    global operandMap


    if command_type == "LOAD_TO_REGISTER":
        existingCommand = True
        # commandMap.append(index)
        commandMap.append(command_operands[0] + 0x10)
        operandMap.append(command_operands[1])

    elif command_type == "WAIT_LONG":
        # vgmSamples = int.from_bytes(command_operands[0]+ command_operands[1], byteorder='little')
        vgmSamples = (command_operands[1] << 8) | command_operands[0]  # should now be a 16 bit number little endian
        vgmSamplesPerFrame = 44100 / 51.9 # samples per second / 60frames per second  (60 was too slow... is it in pal or something)
        frameCount = round(vgmSamples / vgmSamplesPerFrame)
        commandMap.append(0x00)
        operandMap.append(frameCount)

    elif command_type == "END_OF_SONG":
        commandMap.append(0xFF)
        operandMap.append(0x00)

    return


# call main
main()
