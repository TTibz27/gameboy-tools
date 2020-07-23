import argparse
from PIL import Image

parser = argparse.ArgumentParser(description='Convert PNG to GB compatible 2 bit per pixel binary.')
parser.add_argument('filename', help='input PNG file')

args = parser.parse_args()
print("attempting to read {}".format(args.filename))
img = Image.open(args.filename)
mode = img.mode
print("Mode: {}".format(mode))


if mode == "L":
    print("Black and white mode")
if mode == "P":
    print("Pallete Mode")
    palette = img.palette

    print("Palette Color Mode: {}".format(palette.mode))
    colors = palette
    print("Palette Colors: {}".format(palette))



if mode == "RGB":
    print("RGB MODE")
if mode == "RGBA":
    print("RGBA Mode")


def remove_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im