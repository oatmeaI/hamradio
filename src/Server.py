from plexapi.server import PlexServer
from Config import Config


def server():
    return PlexServer(Config.server, Config.token)
