#!/usr/bin/env python3

import sys
import os
from time import sleep
from PIL import Image
from irc_client import IrcClient as irc
from config import *

if ALPHA_BLENDING:
    BLENDING_COLOR = BLENDING_COLOR.strip("#")
    BLENDING_COLOR = tuple(int(BLENDING_COLOR[i:i+2], 16) for i in (0, 2, 4))

def draw(source, start_x, start_y) -> None:
    pic = Image.open(source)
    bands = pic.getbands()
    if bands == ('R','G','B'): bands = 'rgb'
    elif bands == ('R','G','B','A'): bands = 'rgba'
    elif bands == ('1',): bands = 'bw'
    else: raise RuntimeError('Image type could not be identified')

    for y in range(pic.size[1]):
        for x in range(pic.size[0]):
            pixel = (x, pic.size[1] - y -1)
            cords = (x + start_x, y + start_y)
            c = None

            if bands == 'rgb':
                r, g, b = pic.getpixel(pixel)
                if OMMIT_WHITE:
                    if r > OMMIT_TRESHOLD and g > OMMIT_TRESHOLD and b > OMMIT_TRESHOLD:
                        continue

            elif bands == 'rgba':
                if ALPHA_BLENDING:
                    src_r, src_g, src_b, src_a = pic.getpixel(pixel)
                    dst_r, dst_g, dst_b = BLENDING_COLOR

                    r = (src_r * src_a) + (dst_r * (1 - src_a))
                    g = (src_g * src_a) + (dst_g * (1 - src_a))
                    b = (src_b * src_a) + (dst_b * (1 - src_a))
                else:
                    r, g, b, a = pic.getpixel(pixel)
                    if a < 15: continue
                    elif OMMIT_WHITE:
                        if r > OMMIT_TRESHOLD and g > OMMIT_TRESHOLD and b > OMMIT_TRESHOLD:
                            continue

            elif bands == 'bw':
                c = pic.getpixel(pixel)
                if c == 255 and OMMIT_WHITE:
                    continue

            if c != None:
                if c == 0: color = '000000'
                else: color = 'ffffff'
            else: color = '{:02x}{:02x}{:02x}'.format(r, g, b)

            irc().send_message(f'!{str(cords[0])} {str(cords[1])} #{color}')
            sleep(DELAY)

def main():
    if len(sys.argv) == 2:
        if os.path.isfile(sys.argv[1]):
            irc().connect('irc.twitch.tv', 6697, NAME, OAUTH, CHANNEL)
            try:
                start_x = int(input("Start drawing at X: "))
                start_y = int(input("Start drawing at Y: "))
            except ValueError: sys.exit("Coordinates have to be integer numbers")
            draw(sys.argv[1], start_x, start_y)
            irc().disconnect()
            sys.exit()
        else: sys.exit("File does not exist")
    else: sys.exit("No file path provided")

if __name__ == "__main__": main()
