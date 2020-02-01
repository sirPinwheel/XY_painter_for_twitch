#!/usr/bin/env python3

from PIL import Image
from irc_client import IrcClient as irc
import time
from datetime import datetime
import os
from config import *

pictures = dict()
if os.path.isdir("./img"):
    for element in os.listdir('./img/'):
        if os.path.isfile(f'./img/{element}'):
            pictures[element] = f'./img/{element}'
        else: continue
else: raise RuntimeError('No directory named \'img\'')
if len(pictures) == 0: raise RuntimeError('No files in \'img\'')

irc().connect('irc.twitch.tv', 6697, NAME, OAUTH, CHANNEL)

@irc.handlerfunction
def h_stop(user: str, message: str) -> None:
    if user == NAME and message[:6] == '>stop':
        irc().disconnect()

@irc.handlerfunction
def h_print(user: str, message: str) -> None:
    to_print: str = '{}: {}'.format(user, message)
    date: str = datetime.now().strftime('%H:%M:%S')
    print('[{}] {}'.format(date, to_print))

@irc.handlerfunction
def h_draw(user: str, message: str) -> None:
    if user == NAME and message[:6] == '>draw ':
        command = message.split(' ')
        if len(command) != 4:
            irc().send_message('No such command')
            return
        else:
            try: pic = pictures[command[1]]
            except KeyError:
                irc().send_message('No such file')
                return

        try:
            x_cord = int(command[2])
            y_cord = int(command[3])
        except ValueError:
            irc().send_message('Wrong coordinates')
            return

        pic = Image.open(pic)

        bands = pic.getbands()
        if bands == ('R','G','B'): bands = 'rgb'
        elif bands == ('R','G','B','A'): bands = 'rgba'
        elif bands == ('1',): bands = 'bw'
        else: raise RuntimeError('Image type could not be identified')

        for y in range(pic.size[1]):
            for x in range(pic.size[0]):
                pixel = (x, pic.size[1] - y -1)
                cords = (x + x_cord, y + y_cord)
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
                time.sleep(1.7)
