# XY_painter_for_twitch
A script that connects to twitch channel's chat and draws an image pixel by pixel
using ``!X Y #RRGGBB`` format.

# Disclaimer
I am in no way responsible for anything that happens to your account, i have set the
message delay so that it complies with Twitch's message limit for regular users, at this time
it is 20 messages in 30 seconds, if you decide to change the delay you might get banned.
Do it at your own risk, the drawing process takes a lot of time that's why there's a way to
exclude the white and near-white pixels from the picture.

# How to configure
The program was designed to work with one channel, but there's no reason for it to not work with
a different one that's using the same format for drawing pixels.

To use it first you'll need to configure it, all the settings are in the config.py file:

``NAME`` that's just the nickname of the account you want to use for sending messages
be sure to type it in all lowercase

``OAUTH`` is an authorization token, it is needed for twitch server to accept messages
from the bot, you can get it on ``twitchapps.com/tmi``. Before you connect the oauth generator
make sure you're logged in to the account you want to use with the bot and be sure to
include the ``oauth:`` part of the token in the config file.

``CHANNEL`` just the name of the channel where the messages are to be sent, including the ``#``
at the beginning

``OMMIT_WHITE`` and ``OMMIT_TRESHOLD`` are quite important for faster drawing, first one is
just a switch, if it's ``True`` then the skipping of the near-white colors is enabled,
this function makes it so the bot doesn't send chat messages for white or near-white pixels
letting it skip large portions of the picture.

The other variable is a whole number between 0 and 255, it provides a treshold for the bot,
if all RGB components of the pixel are above the treshold it gets skipped, setting it too low
may degrade the quality if the picture is very bright, it's best to set it around 240.
In case ``OMMIT_WHITE`` is set to ``False`` then ``OMMIT_TRESHOLD`` doesn't do anything.

``ALPHA_BLENDING`` is a function that takes into account pixels with opacity, due to the
fact that the bot is unable to see the canvas its drawing on it is also unable to properly
display transparency, basically it doesn't know what color the background is. If ALPHA_BLENDING
is disabled (``False``) the bot will just draw every pixel fully opaque, but that can lead to some weird
looking images, that why ALPHA_BLENDING should be enabled (``True``).

``BLENDING_COLOR`` this is what the bot will assume the background color is, it should be set to the
color of the canvas of the stream, most streams will likely use white. The color is a standard
hex code, you can use any color picker to get the value you need

``DELAY`` BE CAREFUL with changing this option, it's a delay between messages, Twitch has a
limit to how many messages one account can send, meaning that if you decrease this then the
picture will be drawn quicker, but you risk getting your account banned.
As said in the disclaimer section, i am in no way responsible for anything that happens to
your account, use this bot at your own risk, that said i've been using it for hours non-stop
with the limit set to ``1.7`` and it was completely fine.

# How to use
You will need a Python interpreter, all versions of python 3 should work, but i only tested
it on versions 3.6 and 3.8. You can download Python from ``python.org``, when you're done
find a picture you want to draw and simply drag and drop it on the main.py file, it will open
a command line interface where it will ask you for starting coordinates, put in X and Y confirming
each with ``enter``, the process of drawing will start automatically.
