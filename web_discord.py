#!/usr/bin/env python3
import asyncio
from json import loads
import sys
from pprint import pprint
from configparser import ConfigParser
from shutil import move
import discord

config = ConfigParser()
config.read(sys.argv[1:])

channelid = int(config.get('discord', 'channelid'))
guildid = int(config.get('discord', 'guildid'))
output_file = config.get('web', 'out')

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if (message.author == client.user) or (message.channel.id != channelid) or (message.guild.id != guildid):
        return

    #pprint(message)

    displayed_message = '<%s> %s' % (
            message.author.name, message.content)
    
    print('Message: %s' % displayed_message)
    
    f = open(output_file + '.new', 'wb')
    f.write(displayed_message.encode('utf-8'))
    f.close()
    move(output_file + '.new', output_file)

client.run(config.get('discord', 'token'))
