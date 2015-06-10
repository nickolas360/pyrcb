# pyrcb
`pyrcb` is a simple library for Python IRC bots. It isn't a full implementation
of IRC; instead, it provides just enough to write IRC bots. `pyrcb` is
compatible with Python 2 and 3.

To use it, import `pyrcb` and create a class that inherits `IrcBot`. Override
one or more of the events. (You will most likely want to call `send()` from
within the events.) Create an instance of your class and call `connect()`,
`register()`, optionally `join()`, and `listen()` (or `listen_async()`—see
below).

See [examples](examples) for examples.

##### New in version 1.4.2:
* Fixed errors when PART or QUIT messages are received with no message.

##### New in version 1.4.0:
* Added `password()` function, which sets a connection password and identifies
  with NickServ.

##### New in version 1.3.0:
* Added `nick()` and `on_nick()` functions.

### Constructor
`IrcBot(debug_print=False, print_function=print)`  
Creates a new IRC bot. If `debug_print` is `True`, all communication with the
IRC server will be sent to `print_function`.

### Events
`on_join(self, nickname, channel)`  
Called when a user joins a channel.

`on_part(self, nickname, channel, message)`  
Called when a user leaves a channel. `message` is the part message.

`on_quit(self, nickname, message)`  
Called when a user quits. `message` is the quit message.

`on_kick(self, nickname, channel, target, is_self)`  
Called when a user is kicked. `nickname` is the user doing the kicking and
`target` is the person being kicked. `is_self` specifies whether or not this
bot is the one being kicked.

`on_nick(self. nickname, new_nickname, is_self)`  
Called when a user changes their nickname. `is_self` specifies whether or not
this bot's nickname is the one being changed.

`on_names(self, channel, names)`  
Called when the server sends a list of names for the specified channel. `names`
is a list of nicknames. If no names were found in reponse to a names request,
`channel` and `names` will be set to `None`.

`on_message(self, message, nickname, target, is_query)`  
Called when a message is received. `target` is to whom/what the bot should
reply. If the message is in a channel, `target` is the channel. If the message
is in a private query, `target` is the other user.

`on_notice(self, message, nickname, target, is_query)`  
The same as `on_message()`, except for notices.

`on_other(self, nickname, command, args)`  
Called when a message not listed above is received. `nickname` is either the
nickname of the user who sent the message or the server name. `command` is the
IRC command or numeric reply. `args` is a list of the message's arguments,
including a trailing argument if present.

### Methods
`connect(hostname, port, use_ssl=False, ca_certs=None)`  
Connects to the specified `hostname` and `port`. `use_ssl` specifies whether or
not an SSL connection should be established. `ca_certs` is an optional path to
a valid [CA certificates file][1], such as [Mozilla's CA certificates][2] from
[curl.haxx.se](http://curl.haxx.se/docs/caextract.html).
[1]: https://docs.python.org/3.4/library/ssl.html#ca-certificates
[2]: https://raw.githubusercontent.com/bagder/ca-bundle/master/ca-bundle.crt

`password(password)`  
Sets a connection password. Can also be used to identify with NickServ. This
must be called before `register()`.

`register(nickname)`  
Sends the IRC server nickname and user information. Raises a `ValueError` if
the specified nickname is already in use.

`join(channel)`  
Joins the specified channel.

`part(channel, message=None)`  
Leaves the specified channel with the specified part message.

`quit(message=None)`  
Closes connection to the IRC server with the specified quit message.

`nick(new_nickname)`  
Changes the bot's nickname.

`names(channel)`  
Requests a list of names for the current channel.

`send(target, message)`  
Sends `target` the specified message. `target` can be a channel or user.

`send_notice(target, message)`  
The same as `send()`, except for notices.

`send_raw(message)`  
Sends a raw IRC message/command. Useful if you need to send a message not
listed above.

`listen(async_events=False)`  
Listens for incoming messages, calling events when appropriate. This method is
blocking and returns when connection to the IRC server is lost. If
`async_events` is `True`, events will be called on a separate thread and will
not block additional messages from being received.

`listen_async(callback=None, async_events=False)`  
The same as `listen()`, except messages are received on a separate thread. This
method is non-blocking and calls the optional function `callback` when
connecion to the IRC server is lost. The thread started by this method is a
daemon thread and will thus not keep the program running.

`is_alive()`  
Returns whether or not the IRC bot is connected to the IRC server. If you need
infinite loops, use `while bot.is_alive():` instead of `while True:`, so the
loop will stop when connection to the server is lost.

### Instance Attributes
These attributes should (generally) not be modified.

`IrcBot().hostname`  
The hostname of the IRC server.

`IrcBot().port`  
The port of the IRC server.

`IrcBot().channels`  
A list of channels the bot is in.

`IrcBot().nickname`  
The nickname of the bot.
