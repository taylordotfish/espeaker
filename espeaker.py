#!/usr/bin/env python3
# Copyright (C) 2015-2016, 2021 taylor.fish <contact@taylor.fish>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyrcb2 import IRCBot, Event
from getpass import getpass
from xml.sax.saxutils import escape
import asyncio
import conf
import sys

__version__ = "0.3.0"

USAGE = """\
Usage: espeaker <port> <irc-host> <irc-port> [--ssl] <nickname> <channel>\
"""

SSML_TEMPLATE = """
<voice name="{0}">
    <prosody pitch="{1}">
        {2}
    </prosody>
</voice>
"""


class ESpeaker:
    def __init__(self, channel, port, **kwargs):
        self.bot = IRCBot(**kwargs)
        self.bot.load_events(self)
        self.channel = channel
        self.port = port
        self.server = None
        self.clients = set()

    async def start_server(self):
        def client_connected(reader, writer):
            self.clients.add((reader, writer))
            writer.write(conf.connect_message.encode("utf8"))
        self.server = await asyncio.start_server(
            client_connected, "", self.port,
        )

    async def stop_server(self):
        for reader, writer in self.clients:
            writer.close()
        for reader, writer in self.clients:
            try:
                await writer.drain()
            except ConnectionError:
                pass
        self.server.close()
        await self.server.wait_closed()

    async def broadcast(self, message):
        message_bytes = message.encode("utf8")
        disconnected = set()
        for reader, writer in self.clients:
            writer.write(message_bytes)
        for reader, writer in self.clients:
            try:
                await writer.drain()
            except (ConnectionError, TimeoutError):
                disconnected.add((reader, writer))
        self.clients -= disconnected

    @Event.privmsg
    async def on_privmsg(self, sender, channel, message):
        if channel is None:
            return
        voice, pitch = get_voice(sender)
        ssml_data = SSML_TEMPLATE.format(voice, pitch, escape(message))
        print("SSML data:", ssml_data[1:], end="")
        await self.broadcast(ssml_data)

    async def run(self, hostname, port, ssl, nickname, password):
        async def init():
            await self.bot.connect(hostname, port, ssl=ssl)
            await self.bot.register(nickname, password=password)
            await self.bot.join(self.channel)
            await self.start_server()
        await self.bot.run(init())


def get_voice(nickname):
    if nickname in conf.voices:
        return conf.voices[nickname]
    return conf.voices.default_factory()


def invalid_args():
    print(USAGE, file=sys.stderr)
    return 1


def main(argv):
    if not (6 <= len(argv) <= 7):
        return invalid_args()
    ssl = False
    if len(argv) == 7:
        if argv[4] != "--ssl":
            return invalid_args()
        ssl = True
        del argv[4]

    port, irc_host, irc_port, nickname, channel = argv[1:]
    port, irc_port = int(port), int(irc_port)

    print("Password (empty for none): ", end="", file=sys.stderr, flush=True)
    password = getpass("") if sys.stdin.isatty() else input()

    async def run():
        espeaker = ESpeaker(channel, port, log_communication=True)
        await espeaker.run(irc_host, irc_port, ssl, nickname, password)

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
