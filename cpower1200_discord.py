#!/usr/bin/env python3
import asyncio
from json import loads
import sys
from pprint import pprint
from configparser import ConfigParser
from cpower1200 import *

import discord

config = ConfigParser()
config.read(sys.argv[1:])

channelid = int(config.get('discord', 'channelid'))
guildid = int(config.get('discord', 'guildid'))

client = discord.Client()
sign = CPower1200(config.get('cpower1200', 'port'))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # Set up the sign
    sign.set_clock()
    sign.send_window(
        dict(x=0 , y=0, h=8, w=32), # window 0: top left: time
        dict(x=32, y=0, h=8, w=32), # window 1: top right: date
        dict(x=0 , y=8, h=8, w=64)  # window 2: bottom: messages
    )
    sign.send_clock(0, calendar=CALENDAR_GREGORIAN, multiline=False, display_year=False, display_hour=False, display_minute=False, display_second=False, red=0)
    sign.send_clock(1, calendar=CALENDAR_GREGORIAN, multiline=False, display_year=False, display_month=False, display_day=False, display_second=False, green=0)

    sign.send_text(2, sign.format_text('waiting for dank memes...', GREEN, 0), speed=4)

@client.event
async def on_message(message):
    if (message.author == client.user) or (message.channel.id != channelid) or (message.guild.id != guildid):
        return

    #pprint(message)

    displayed_message = '<%s> %s' % (
            message.author.name, message.content)
    
    displayed_message = displayed_message.encode('ascii', 'ignore')
    print('Message: %s' % displayed_message)
    
    # Now send this to sign
    sign.send_text(2, sign.format_text(displayed_message, GREEN, 0), speed=4)
    sign.set_clock()

client.run(config.get('discord', 'token'))
