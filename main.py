#!/usr/bin/env python3

import sys
import os
from time import sleep
from PIL import Image
from irc_client import IrcClient as irc
from config import *

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
            irc.disconnect()
            sys.exit()
        else: sys.exit("File does not exist")
    else: sys.exit("No file path provided")

if __name__ == "__main__": main()
