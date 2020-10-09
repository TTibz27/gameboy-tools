import argparse
import png
from PIL import Image
import numpy
import pallete_mode

######################################################################################
parser = argparse.ArgumentParser(description='Convert PNG to GB compatible 2 bit per pixel binary.')
parser.add_argument('infile', help='input PNG file')
parser.add_argument('outfile', help='output GB file')

args = parser.parse_args()
print("attempting to read {}".format(args.infile))
img = Image.open(args.infile)
mode = img.mode
print("Mode: {}".format(mode))

if mode == "P":
    print("Pallete Mode")
    reader = png.Reader(args.infile)
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

        pallete_mode.convert_4_color_palette(dataArray, width, height, args.outfile)


if mode == "RGB":
    print("RGB MODE")