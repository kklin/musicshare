# musicshare
#### DJ-ing, made democratic!

Video demo:  https://www.youtube.com/watch?v=GKnQUizjkbU
That video is pretty outdated now. It doesn't show things like adding songs and the client console, among other things.

This set of programs allows users to create a designated playback server, and
connect multiple clients that together decide what songs should be played.

It's still in its most simple form, but this could easily be extended to
situations such as coffee shops and parties. Imagine if upon walking into a
coffeeshop your phone automatically detected there was a Musicshare server
running and prompted you to vote on the coffeeshop playlist.

Or, for a more passive approach, your phone could simple send your Spotify profile to the
server, and the server could generate a playlist based on the Spotify profiles
of the connected clients. With the rich data provided by Spotify and Echonest,
this kind of stuff is possible.


#### TODO
Short term:
- [ ] Add smarter playlist generation
- [x] Allow users to add songs suggestions to the playlist
- [x] Allow server to skip/pause songs (idea of master client)
- [ ] Create GUI for client
- [x] Automatically connect clients when a server is available


Long term:
- [ ] Create mobile version
- [ ] Integrate Bitcoin to turn Musicshare into a jukebox
- [ ] Integrate into Raspberry Pi
