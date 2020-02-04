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

            if bands == 'rgb':
                r, g, b = pic.getpixel(pixel)
                if OMMIT_WHITE and r > OMMIT_TRESHOLD and g > OMMIT_TRESHOLD and b > OMMIT_TRESHOLD: continue

            elif bands == 'rgba':
                if ALPHA_BLENDING:
                    src_r, src_g, src_b, src_a = pic.getpixel(pixel)
                    dst_r, dst_g, dst_b = BLENDING_COLOR
                    src_a = src_a / 255
                    if src_a < 0.05: continue

                    r = int((src_r * src_a) + (dst_r * (1 - src_a)))
                    g = int((src_g * src_a) + (dst_g * (1 - src_a)))
                    b = int((src_b * src_a) + (dst_b * (1 - src_a)))

                    if OMMIT_WHITE and r > OMMIT_TRESHOLD and g > OMMIT_TRESHOLD and b > OMMIT_TRESHOLD: continue
                else:
                    r, g, b, a = pic.getpixel(pixel)
                    if a < 15: continue
                    if OMMIT_WHITE and r > OMMIT_TRESHOLD and g > OMMIT_TRESHOLD and b > OMMIT_TRESHOLD: continue

            elif bands == 'bw':
                c = pic.getpixel(pixel)

                if OMMIT_WHITE:
                    if c == 255: continue
                    else: r, g, b = (0, 0, 0)
                else:
                    if c == 255: r, g, b = (255, 255, 255)
                    else: r, g, b = (0, 0, 0)

            else: raise RuntimeError("unsupported color band format")

            color = '{:02x}{:02x}{:02x}'.format(r, g, b)

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
            print(f"drawing {sys.argv[1]} at {start_x} x {start_y} ", end="", flush=True)
            draw(sys.argv[1], start_x, start_y)
            print("done")
            irc().disconnect()
            sys.exit()
        else: sys.exit("File does not exist")
    else: sys.exit("No file path provided")

if __name__ == "__main__": main()
