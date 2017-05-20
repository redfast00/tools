#!/usr/bin/env python3
# This code is not pretty, but it works
# This program generates an arrowified image from a source image, check out arrowart.png
from PIL import Image, ImageDraw
import operator
from pprint import pprint
import argparse

base_width = 10
arrow_base_height = 15
arrow_point_height = 15
margin = (20,20)
do_outline = True
outline = (0, 0, 0) # black
background_color  = (255, 255, 255) # white

arrow_width = base_width / 2
total_arrow_height = arrow_base_height + arrow_point_height
total_arrow_width = 2 * base_width

arrow = [
    (0, 0),
    (arrow_base_height, 0),
    (arrow_base_height, arrow_width),
    (arrow_base_height + arrow_point_height, - arrow_width),
    (arrow_base_height, -3 * arrow_width),
    (arrow_base_height, - base_width),
    (0, - base_width)
]

def draw_arrow(coords, color):
    if do_outline:
        draw.polygon(coords, fill=color, outline=outline)
    else:
        draw.polygon(coords, fill=color)

def to_real_coordinates(coords):
    # translates the coords to pixels on the picture
    return translate(coords, margin)

def translate(coords, vector):
    # Translates a list of coordinate tuples over a vector tuple
    t_coords = []
    for cord in coords:
        t_coords.append(tuple(map(operator.add, cord, vector)))
    return t_coords

def mirror(coords):
    # Takes a list of coordinate tuples and mirrors it across the first element of
    #    the first tuple
    # Formula: 2 * base - original
    m_coords = []
    base = coords[0]
    double_base = tuple(map(operator.mul, base, len(base)* (2,) ))
    for cord in coords:
        m_coords.append(tuple(map(operator.sub, double_base, cord)))
    return m_coords

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make art.')
    parser.add_argument('infile',type=argparse.FileType('r'))
    parser.add_argument('--outfile', type=argparse.FileType('wb'), default=None)
    args = parser.parse_args()
    orig = Image.open(args.infile).transpose(Image.ROTATE_90)
    pix = orig.load()
    new_size = (1024,1024)
    actual_size = (new_size[0] + 2 * margin[0], new_size[1] + 2*margin[1])
    im = Image.new("RGB", actual_size, background_color)
    draw = ImageDraw.Draw(im)
    m_arrow = mirror(arrow)
    for i in range(new_size[0] / total_arrow_height):
        for j in range((new_size[1] / total_arrow_width)):
            color = pix[
                i * total_arrow_height * orig.size[0] / new_size[0],
                j * total_arrow_width * orig.size[1] / new_size[1]
            ]
            # calculate and draw arrow
            coords = translate(arrow, (i * total_arrow_height, j * total_arrow_width))
            real_coords = to_real_coordinates(coords)
            draw_arrow(real_coords, color)
            # calculate and draw mirrored arrow
            coords = translate(m_arrow, (arrow_base_height + i * total_arrow_height, j * total_arrow_width))
            real_coords = to_real_coordinates(coords)
            draw_arrow(real_coords, color)

    im = im.transpose(Image.ROTATE_270)
    im.show()
    if args.outfile:
        im.save(args.outfile)