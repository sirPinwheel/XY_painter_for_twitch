# XY_painter_for_twitch
A script that connects to twitch channel's chat and draws an image pixel by pixel using [X Y #RRGGBB] format

# Disclaimer
I am in no way shape or form responsible for anything that happens to your account, i have set
the message delay so that i complies with Twitch's message limit for regular user, at this time
it is 20 messages in 30 seconds, if you decide to change the delay you might get banned

# How to use
The program was designed to work with one channel, but there's no reason for it to not wortk with
a different one that's using the same format for drawing pixels, to use it first put a picture
in the "pic" directory, then run the bot, after it connects to the chat you can type in a command
that will make it start drawing an image

``>draw NameOfMyPicture.png 20 20``

You will need to provide a full name of the file as well as the starting coordinates
