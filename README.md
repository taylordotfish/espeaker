espeaker
========

Version 0.3.0

**espeaker** is an IRC bot which allows users to listen to IRC with the
text-to-speech program [espeak]. It converts IRC messages into SSML data that
can be piped to and read by espeak. Users can be given unique voices.

[espeak]: https://en.wikipedia.org/wiki/ESpeak

espeaker runs over a network socket, allowing people to connect to it and pipe
the data to espeak. Use the command ``nc <espeaker-host> <espeaker-port> |
espeak -m`` to connect and listen to espeaker. Option ``-m`` enables SSML
support in espeak.

Edit ``conf.py`` to give users espeak voices. See ``espeak --voices`` and
``espeak --voices=variant`` to see what voices and variants you can use.

Usage
-----

``espeaker <port> <irc-host> <irc-port> [--ssl] <nickname> <channel>``

``<port>`` is the port the espeaker server should run on, not the port of the
IRC server (which is ``<irc-port>``).

Use ``--ssl`` to connect to the IRC server with SSL/TLS.

espeaker will ask for a NickServ password when started. Supply an empty
password if you don't want to use one.

What's new
----------

Version 0.3.0:

* espeaker now works with (and requires) [pyrcb2] v0.6.

Version 0.2.0:

* Switched to pyrcb2.

Dependencies
------------

* Python ≥ 3.7
* Python package: [pyrcb2]

Run ``pip3 install -r requirements.txt`` to install the Python packages. You
can also use ``requirements.freeze.txt`` instead to install specific versions
of the dependencies that have been verified to work.

[pyrcb2]: https://pypi.org/project/pyrcb2

License
-------

espeaker is licensed under version 2 of the Apache License.
See [LICENSE](LICENSE).
