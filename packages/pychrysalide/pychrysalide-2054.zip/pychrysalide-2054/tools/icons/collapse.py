#!/usr/bin/env python

import cairo
import sys


WIDTH, HEIGHT = 256, 256
WIDTH, HEIGHT = 12, 12

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ctx.scale(WIDTH, HEIGHT)

if len(sys.argv) > 1 and sys.argv[1] == '--dark':
    ctx.set_source_rgb(1.0, 1.0, 1.0)
    dark = '_dark'
else:
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    dark = ''

ctx.move_to(0.4, 0.4)
ctx.line_to(0.4, 0.0)
ctx.line_to(0.0, 0.4)

ctx.fill()

ctx.move_to(0.6, 0.4)
ctx.line_to(0.6, 0.0)
ctx.line_to(1.0, 0.4)

ctx.fill()

ctx.move_to(0.6, 0.6)
ctx.line_to(1.0, 0.6)
ctx.line_to(0.6, 1.0)

ctx.fill()

ctx.move_to(0.4, 0.6)
ctx.line_to(0.4, 1.0)
ctx.line_to(0.0, 0.6)

ctx.fill()

surface.write_to_png('../../pixmaps/collapse%s.png' % dark)
