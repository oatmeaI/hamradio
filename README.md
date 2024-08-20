# HamRadio for Plex(Amp)

custom radios for plex music libraries

## what?

this project creates custom playqueues of your plex music based on complex rules you can define.
for example: "play a mix of songs I've heard and ones I haven't, preferring songs I haven't heard, and use sonic analysis to make sure each song flows into the next"

## why?

I love Plex's Radios and Plexamp's Guest DJs, but I want _more_ control. specifically I wanted to create the first example above - I wanted to shuffle tracks I've never heard into a queue of tracks I know I like, using sonic analysis data to make sure they flow well.

## how?

(note: this guide is very rough right now; I'll take some time later to create a more in depth user guide).

0. Install dependencies however you like - I'm using [Poetry](https://python-poetry.org/), but you don't have to. The only external dependencies for HamRadio are [python-plexapi](https://github.com/pkkid/python-plexapi) and [flask](https://flask.palletsprojects.com/en/3.0.x/)
1. Configure customradio: rename `sample-config.toml` to `config.toml` and fill in the values.
2. Configure a station: the sample `stations.toml` file in this repo demonstrates station config; you can tweak it or create your own.
3. Run `poetry run flask --app webserver run --host=0.0.0.0`
4. Make a HTTP GET request to `http://[YOUR-SERVER-ADDRESS]?station=[STATION-NAME]`

HamRadio will try to use the Plex Remote Control API to tell your client to start playing the radio it creates, but if it fails, it will instead return a deep link that, when opened, will launch PlexAmp and start playing the queue. 

## roadmap

this project is obviously extremely early in development, and there's a lot of work to be done. in no particular order:

- [ ] pass queue length, client address in request params
- [ ] additional code cleanup
- [ ] address various TODOs
- [ ] better UX when we can connect to the client remote control
- [ ] improve filtering and sorting: I'd like to add more operators to the Filter class, improve the Sort interface
- [ ] improve documentation, especially around station definitions
- [ ] add an option to create a playlist instead of a playqueue
- [ ] add deeplink options for plex as well as plexamp
- [ ] add validation of config files & error handling
- [ ] add type hinting
- [ ] tests

### done!
- [x] add an argument to specify which station to load: currently you can define as many stations as you want, but we'll only ever use the first one
- [x] figure out if we can work around the plex remote control api, since it's a little unreliable, and doesn't work when you're not on LAN
- [x] clean up & refactor code: everything is obviously in one giant file right now, which is not ideal, and I wrote it all in one night - so there's stuff to be cleaned up, commented, etc.
- [x] add an abstraction layer on top of the Plex property names (ie. `viewCount` doesn't make much sense for music)
- [x] improve filtering so that we don't play tracks from the same album back to back
