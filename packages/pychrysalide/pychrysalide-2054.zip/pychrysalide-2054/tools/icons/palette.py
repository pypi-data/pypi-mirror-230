#!/usr/bin/env python

import math
import cairo


WIDTH, HEIGHT = 256, 256
WIDTH, HEIGHT = 12, 12

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ctx.scale(WIDTH, HEIGHT)

ctx.arc(0.5, 0.5, 0.40, 0, 2 * math.pi)
ctx.set_source_rgb(1.0, 1.0, 1.0)
ctx.fill()

colors = [
    'fefe33',
    'fabc02',
    'fb9902',
    'fd5308',
    'fe2712',
    'a7194b',
    '8601af',
    '3d01a4',
    '0247fe',
    '0391ce',
    '66b032',
    'd0ea2b'
]

angle = (2 * math.pi) / len(colors)

for i in range(len(colors)):

    hval = int(colors[i], 16)

    red   = ((hval & 0xff0000) >> 16) / 256
    green = ((hval & 0x00ff00) >>  8) / 256
    blue  = ((hval & 0x0000ff) >>  0) / 256

    start = angle / 2 - i * angle

    ctx.arc(0.5, 0.5, 0.5, start - angle, start)

    ctx.arc_negative(0.5, 0.5, 0.15, start, start - angle)

    ctx.set_source_rgb(red, green, blue)
    ctx.fill()

surface.write_to_png('../../pixmaps/palette.png')
