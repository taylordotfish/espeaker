#!/usr/bin/env python3
# Copyright (C) 2015=2016 taylor.fish <contact@taylor.fish>
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

from pyrcb import IRCBot
from getpass import getpass
from xml.sax.saxutils import escape
import conf
import socket
import sys

__version__ = "0.1.3"

USAGE = "Usage: espeaker <port> <irc-host> <irc-port> <nickname> <channel>"

SSML_TEMPLATE = """
<voice name="{0}">
    <prosody pitch="{1}">
        {2}
    </prosody>
</voice>
"""


class ESpeaker(IRCBot):
    def __init__(self, *args, **kwargs):
        super(ESpeaker, self).__init__(*args, **kwargs)
        self.clients = []

    def start_server(self, port):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("", port))
            s.listen(5)
            while self.alive:
                client, address = s.accept()
                client.sendall(conf.connect_message.encode("utf8"))
                self.clients.append(client)
        finally:
            s.shutdown(socket.SHUT_RDWR)
            s.close()

    def broadcast(self, message):
        disconnected = []
        for client in self.clients:
            try:
                client.sendall(message)
            except (ConnectionError, TimeoutError):
                disconnected.append(client)
        for client in disconnected:
            self.clients.remove(client)

    def on_message(self, message, nickname, channel, is_query):
        if is_query:
            return
        voice, pitch = conf.voices[nickname]
        ssml_data = SSML_TEMPLATE.format(voice, pitch, escape(message))
        self.broadcast(ssml_data.encode("utf8"))
        print("<{0}> {1}".format(nickname, message))


def main():
    if len(sys.argv[1:]) != 5:
        print(USAGE)
        return

    port, irc_host, irc_port, nickname, channel = sys.argv[1:]
    port, irc_port = int(port), int(irc_port)

    print("Password (empty for none): ", end="", file=sys.stderr, flush=True)
    password = getpass("") if sys.stdin.isatty() else input()

    bot = ESpeaker()
    bot.connect(irc_host, irc_port)
    if password:
        bot.password(password)
    bot.register(nickname)
    bot.join(channel)

    def stop_server():
        # Connect to server so accept() call returns.
        s = socket.socket()
        s.connect(("", port))
        s.shutdown(socket.SHUT_RDWR)
        s.close()

    bot.listen_async(callback=stop_server)
    bot.start_server(port)
    print("Disconnected from server.")

if __name__ == "__main__":
    main()
