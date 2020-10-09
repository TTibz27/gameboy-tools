import argparse
import png
from PIL import Image
import numpy

##########################################################################
def write_to_file(filename, byte_array_list):
    print("Writing file {}!".format(filename))
    output = bytearray()
    for listEntry in byte_array_list:
        output.extend(listEntry)
    file = open(filename,"wb")
    file.write(output)
############################################################################
def convert_4_color_palette (inData, inWidth, inHeight):
    inData.shape = inHeight, inWidth

    tile_index_y = 0
    tile_count = 0
    unique_tiles = []
    tile_map = []

    unique_tiles.append(bytearray(16)) # add a blank first tile
    while (tile_index_y * 8) < inHeight:
        tile_index_x = 0

        while (tile_index_x *8) < inWidth:
            # ---------------- Start of a new tile -------------------------------------
            current_tile = bytearray()
            tile_count += 1
            # Push new data to current tile
            for pixel_y in range (8):
                y = (tile_index_y * 8) + pixel_y

                high_byte = 0
                low_byte = 0
                for pixel_x in range (8):
                    # Shift left before adding bits. shouldn't matter if its zero.
                    low_byte = low_byte << 1
                    high_byte = high_byte << 1

                    x = (tile_index_x * 8) + pixel_x
                    val = inData[y][x] # numpy is row column order
                    # print("tile - x: {}  y:{}  | val - {}".format(pixel_x,pixel_y,val))

                    if val == 3:
                        low_byte += 1
                        high_byte += 1
                    elif val == 2:
                        high_byte += 1
                    elif val == 1:
                        low_byte += 1

                current_tile.extend(low_byte.to_bytes(length=1,byteorder='little'))
                current_tile.extend(high_byte.to_bytes(length=1,byteorder='little'))
            # Check if tile is unique
            tile_exists = False
            for index, tile in enumerate(unique_tiles):
                if tile == current_tile:
                    tile_exists = True
                    currentTileIndex = index

            if tile_exists == False:
                print(" x: {} , y: {} | New tile found!".format(tile_index_x, tile_index_y))
                unique_tiles.append(current_tile)
                print(current_tile.hex())
                currentTileIndex = len(unique_tiles) -1
            else:
                print("x: {} , y: {} | Duplicated tile!  index - {}".format(tile_index_x, tile_index_y,currentTileIndex))
                pass

            tile_map.append(currentTileIndex.to_bytes(length=1,byteorder='little'));

            # ----------------NEXT TILE --------------------------------------------------
            tile_index_x += 1
        tile_index_y += 1

#   Write Unique tiles to Bin file, write map to file
    print(" total tiles: {} | unique tiles: {}".format(tile_count, len(unique_tiles)))

    if len(unique_tiles) > 256:
        print("WARNING! unique tiles exceeds normal 256 tile limit")
    elif len(unique_tiles) > 128:
        print("Caution, Unique tiles exceeds half of VRAM limit")
    #Write to file now
    write_to_file("title.bin", unique_tiles)
    write_to_file("title.map.bin", tile_map)
######################################################################################
# This creates a run length encoded output in addition to the standard file.
# to decode, uncompress both high then low, and take a byte from each.
# alledgedly this is how pokemon graphics are compressed as well so hopefully its not too much processor for the 'z80'
def convert_4_color_pallete_run_length_encoded(inData, inWidth, inHeight):
    inData.shape = inHeight, inWidth

    tile_index_y = 0
    tile_count = 0
    unique_tiles = []
    tile_map = []

    output_high_bytes = bytearray()
    output_low_bytes = bytearray()


    unique_tiles.append(bytearray(16))  # add a blank first tile


    while (tile_index_y * 8) < inHeight:
        tile_index_x = 0

        while (tile_index_x * 8) < inWidth:
            # while (tile_index_x * 8) < 8:
            # ---------------- Start of a new tile -------------------------------------
            current_tile_high_bytes = bytearray()
            current_tile_low_bytes = bytearray()
            current_tile_combined = bytearray()

            for pixel_y in range(8):
                y = (tile_index_y * 8) + pixel_y
                high_byte = 0
                low_byte = 0
                for pixel_x in range(8):
                    # Shift left before adding bits. shouldn't matter if its zero.
                    low_byte = low_byte << 1
                    high_byte = high_byte << 1
                    x = (tile_index_x * 8) + pixel_x
                    val = inData[y][x]  # numpy is row column order
                    # print("tile - x: {}  y:{}  | val - {}".format(pixel_x,pixel_y,val))

                    if val == 3:
                        low_byte += 1
                        high_byte += 1
                    elif val == 2:
                        high_byte += 1
                    elif val == 1:
                        low_byte += 1
                # this is the actual data
                current_tile_low_bytes.extend(low_byte.to_bytes(length=1, byteorder='little'))
                current_tile_high_bytes.extend(high_byte.to_bytes(length=1, byteorder='little'))
                # this is just to check if the tile is unique
                current_tile_combined.extend(low_byte.to_bytes(length=1, byteorder='little'))
                current_tile_combined.extend(high_byte.to_bytes(length=1, byteorder='little'))

            # Check if tile is unique
            tile_exists = False
            for index, tile in enumerate(unique_tiles):
                if tile == current_tile_combined:
                    tile_exists = True
                    currentTileIndex = index

            if tile_exists == False:
                print(" x: {} , y: {} | New tile found!".format(tile_index_x, tile_index_y))
                unique_tiles.append(current_tile_combined)
                output_high_bytes.extend(current_tile_high_bytes)
                output_low_bytes.extend(current_tile_low_bytes)
                currentTileIndex = len(unique_tiles) - 1
            else:
                print(
                    "x: {} , y: {} | Duplicated tile!  index - {}".format(tile_index_x, tile_index_y, currentTileIndex))
                pass

            tile_map.append(currentTileIndex.to_bytes(length=1, byteorder='little'))

            # ----------------NEXT TILE --------------------------------------------------
            tile_index_x += 1
        tile_index_y += 1

        #   Write Unique tiles to Bin file, write map to file
        print(" total tiles: {} | unique tiles: {}".format(tile_count, len(unique_tiles)))

        if len(unique_tiles) > 256:
            print("WARNING! unique tiles exceeds normal 256 tile limit")
        elif len(unique_tiles) > 128:
            print("Caution, Unique tiles exceeds half of VRAM limit")
        # Write to file now
        write_to_file("title.bin", unique_tiles)
        write_to_file("title.map.bin", tile_map)

        print ("Starting run length encoding")

        #todo -do the math and stuff


######################################################################################
parser = argparse.ArgumentParser(description='Convert PNG to GB compatible 2 bit per pixel binary.')
parser.add_argument('filename', help='input PNG file')

args = parser.parse_args()
print("attempting to read {}".format(args.filename))
img = Image.open(args.filename)
mode = img.mode
print("Mode: {}".format(mode))


if mode == "P":
    print("Pallete Mode")
    reader = png.Reader(args.filename)
    data = reader.read()
    width = data[0]
    height = data[1]
    # todo - we should have a check to make sure the image is a reasonable (mod8 == 0) size before checking mode
    rows = data[2]
    info = data[3]
    print("Width: {} , Height: {} ".format(width, height))
    print("Data: {}".format(info))
    print(type(rows))

    if len(info['palette']) == 4:
        print("Palette size of 4, starting conversion!")

        data = bytearray()
        for row in rows:
            data.extend(row)

        dataArray = numpy.array(data, dtype=numpy.byte)

        convert_4_color_palette(dataArray, width, height)

    print(" ----------------DUMP------------------")
    i=0


if mode == "RGB":
    print("RGB MODE")




# for row in rows:
