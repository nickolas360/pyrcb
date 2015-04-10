# pyrcb
`pyrcb` is a simple library for Python IRC bots. It isn't a full implementation
of IRC; instead, it provides just enough to write IRC bots. `pyrcb` is
compatible with Python 2 and 3.

To use it, import `pyrcb` and create a class that inherits `IrcBot`. Override
one or more of the events. (You will most likely want to call `send()` from
within the events.) Create an instance of your class and call `connect()`,
`register()`, optionally `join()`, and `listen()` (or `listen_async()` -- see
below). See `examples` for examples.

`IrcBot`'s constructor takes one optional argument, `debug_print`. Setting this
value to `True` will cause all communication with the IRC server to be printed
to standard output.

### Events
`on_join(self, nickname, channel)`  
Called when a user joins a channel.
  
`on_part(self, nickname, channel)`  
Called when a user leaves a channel.
  
`on_quit(self, nickname)`  
Called when a user quits.

`on_kick(self, nickname, channel, target, is_self)`  
Called when a user is kicked. `nickname` is the user who is doing the kicking,
while `target` is the person who is being kicked. `is_self` specifies whether
or not this bot is the one being kicked.

`on_message(self, message, nickname, target, is_query)`  
Called when a message is received. `target` is who/what the bot should reply
to. If the message is in a channel, `target` is the channel. If the message is
in a private query, `target` is the other user.

`on_notice(self, message, nickname, target, is_query)`  
The same as `on_message()`, except for notices.

`on_other(self, message)`  
Called when a message not listed above is received. The message is passed in
raw IRC format.

### Methods
`connect(hostname, port)`  
Connects to the specified `hostname` and `port`.

`register(nickname)`  
Sends the IRC server nickname and user information.

`join(channel)`  
Joins the specified channel.

`part(channel)`  
Leaves the specified channel.

`quit()`  
Closes connection to the IRC server.

`send(target, message)`  
Sends `target` the specified message. `target` can be a channel or user.

`send_raw(message)`  
Sends a raw IRC message (command). Useful if you need to send an IRC message
not listed above.

`listen()`  
Listens for incoming messages, calling events when appropriate. This method is
blocking and returns when connection to the IRC server is lost.

`listen_async(callback=None)`  
Listens for incoming messages on a separate thread, calling events when
appropriate. This method is non-blocking and calls the optional function
`callback` when connection to the IRC server is lost. The thread started by
this method won't keep the program running, so something else needs to. If
nothing else does, use `listen()` instead.

`is_alive()`  
Returns whether or not the IRC bot is connected to the IRC server. If you need
infinite loops, use `while bot.is_alive():` instead of `while True:`, so the
loop will stop when connection to the IRC server is lost.
