from Config import Config
from plexapi.server import PlexServer


def loadSimilar(track):
    if track is None:
        raise Exception("Need a track")
    # TODO: configure distance on per-station basis
    return track.sonicallySimilar(maxDistance=0.5)


def loadRandom(_):
    config = Config
    server = PlexServer(Config.server, Config.token)
    section = server.library.section(config.musicSection)
    return section.searchTracks(maxresults=1, sort="random")[0]


Loaders = {"similar": loadSimilar, "random": loadRandom}
