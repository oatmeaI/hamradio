# HamRadio for Plex(Amp)

custom radios for plex music libraries

## what?

this project creates custom playqueues of your plex music based on complex rules you can define.
for example: "play a mix of songs I've heard and ones I haven't, preferring songs I haven't heard, and use sonic analysis to make sure each song flows into the next"

## why?

I love Plex's Radios and Plexamp's Guest DJs, but i want _more_ control. specifically I wanted to create the first example above - I wanted to shuffle tracks I've never heard into a queue of tracks I know I like, using sonic analysis data to make sure they flow well.

## how?

(note: this guide is very rough right now; I'll take some time later to create a more in depth user guide).

0. Install dependencies however you like - I'm using [Poetry](https://python-poetry.org/), but you don't have to. The only external dependency for customradio is [python-plexapi](https://github.com/pkkid/python-plexapi)
1. Configure customradio: rename `sample-config.toml` to `config.toml` and fill in the values.
2. Configure a station: the sample `stations.toml` file in this repo demonstrates station config; you can tweak it or create your own.
3. Run `poetry run flask --app webserver run --host=0.0.0.0` and watch the magic!

## roadmap

this project is obviously extremely early in development, and there's a lot of work to be done. in no particular order:

- [ ] clean up & refactor code: everything is obviously in one giant file right now, which is not ideal, and I wrote it all in one night - so there's stuff to be cleaned up, commented, etc.
- [ ] add type hinting
- [ ] improve filtering and sorting: I'd like to add more operators to the Filter class, improve the Sort interface
- [x] add an abstraction layer on top of the Plex property names (ie. `viewCount` doesn't make much sense for music)
- [ ] add validation of config files & error handling
- [ ] add an argument to specify which station to load: currently you can define as many stations as you want, but we'll only ever use the first one
- [ ] improve documentation, especially around station definitions
- [ ] add an option to create a playlist instead of a playqueue
- [x] improve filtering so that we don't play tracks from the same album back to back
- [ ] figure out if we can work around the plex remote control api, since it's a little unreliable, and doesn't work when you're not on LAN
