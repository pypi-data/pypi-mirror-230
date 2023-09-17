#!/usr/bin/env python

from os.path import abspath, dirname, join
from PIL import ImageDraw, ImageFont

DIR = dirname(abspath(__file__))

font_path = join(DIR, 'font/600.ttf')
font = ImageFont.truetype(font_path, 20, encoding="utf-8")
COLOR = [0, 0, 0]


def imgbox(img, name_box_li):
  canvas = ImageDraw.Draw(img)

  n = 0
  for (name, box) in name_box_li:

    n += 1
    c = (COLOR[n % 3] + 60) % 256
    COLOR[n % 3] = c
    color = COLOR[:]
    color[((n + 1 + n % 2) % 3)] = 255 - c
    color = tuple(color)
    canvas.text([box[0] + 5, box[1] + 5], name, color, font=font)
    canvas.rectangle(xy=box, fill=None, outline=color, width=1)
  return
