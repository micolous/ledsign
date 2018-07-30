#!/usr/bin/env python3
import asyncio
from json import loads
import sys
from pprint import pprint
from configparser import ConfigParser
# pip install mattermostdriver
from mattermostdriver import Driver
from shutil import move


class Signbot(object):
    def __init__(self, config):
        self._channel = config.get('mattermost', 'channel').lower()
        self._mm = Driver({
            'login_id': config.get('mattermost', 'username'),
            'password': config.get('mattermost', 'password'),
            'url': config.get('mattermost', 'url'),
            'port': config.getint('mattermost', 'port'),
            #'token': self._token,
        })
        self._output_file = config.get('web', 'out')

    def start(self):
        # Set up the sign
        self._mm.login()
        self._mm.init_websocket(self.on_event)
    
    @asyncio.coroutine
    def on_event(self, event):
        "We got a message from the websocket to handle..."
        event = loads(event)
        pprint(event)
        
        if ('event' not in event) or (event['event'] != 'posted') or ('data' not in event) or ('channel_name' not in event['data']) or ('post' not in event['data']):
            # We don't care about anything but channel messages.
            return
        
        # Check if this is for our channel
        channel = event['data']['channel_name'].lower()
        if channel != self._channel:
            # not our channel
            return
        
        # Check if this was the bridge user
        post = loads(event['data']['post'])
        
        displayed_message = ''

        if event['data']['sender_name'] == 'url':
            # This is the bridge bot...
            displayed_message = post['message']
        else:
            displayed_message = '<%s> %s' % (
                event['data']['sender_name'], post['message'])
        
        #displayed_message = displayed_message.encode('ascii', 'ignore')
        #print('Message: %s' % displayed_message)
        
        # Now send this to sign
        #self._sign.send_text(2, self._sign.format_text(displayed_message, GREEN, 0), speed=15)
        #self._sign.set_clock()
        
        f = open(self._output_file + '.new', 'wb')
        f.write(displayed_message.encode('utf-8'))
        f.close()
        
        move(self._output_file + '.new', self._output_file)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('You need to specify a configuration file...')
        sys.exit(1)
    config = ConfigParser()
    config.read(sys.argv[1:])

    signbot = Signbot(config)
    signbot.start()

