NAME = "" # Your username
OAUTH = "" # Your Oauth token
CHANNEL = "" # Name of the channel eg. '#twitch_paints_art'

# If OMMIT_WHITE is True then the program will ommit
# all the pixels that have all the R, G and B components
# higher than OMMIT_TRESHOLD. If False, then all the
# pixels will be drawn, this can increase the time it
# takes to draw the whole picture depending on the ammount
# of pixels above OMMIT_TRESHOLD in the picture.
# Recommended values are True and 240
OMMIT_WHITE = True
OMMIT_TRESHOLD = 240
