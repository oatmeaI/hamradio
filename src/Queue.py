from typing import Optional
from plexapi.server import PlayQueue, Playlist

from Config import Config

BASE_URL = "https://listen.plex.tv/player/playback/playMedia?uri=server://"
EXT = "/com.plexapp.plugins.library/"
QUEUE = "playQueues/"
PLAYLIST = "playlists/"


def guard(fn):
    def wrapped(self, *args):
        if self._queue is None:
            return
        return fn(self, *args)

    return wrapped


class BaseQueue:
    tracks = []
    albums = []
    _queue = None
    _server = None

    def __init__(self, server, key=None):
        self._server = server
        self.key = key

    def _initialize(self, track):
        pass

    @property
    def length(self):
        return len(self.tracks)

    @property
    def id(self) -> Optional[int | float]:
        pass

    @guard
    def _addToQueue(self, track):
        pass

    def addTrack(self, track):
        if self._queue is None:
            self._initialize(track)
        else:
            self._addToQueue(track)
        self.tracks.append(track)
        self.albums.append(track.parentTitle + track.grandparentTitle)

    def empty(self):
        pass

    @property
    def deeplink(self):
        return ""


class Queue(BaseQueue):
    def _initialize(self, track):
        if self._server is None:
            return
        if self.key:
            self._queue = PlayQueue.get(self._server, self.key)
            currentTrack = self._queue.selectedItem
            self.tracks.append(currentTrack)
            self.albums.append(currentTrack.parentTitle + currentTrack.grandparentTitle)
        else:
            self._queue = PlayQueue.create(self._server, [track])

    @property
    @guard
    def id(self):
        return self._queue.playQueueID

    @guard
    def _addToQueue(self, track):
        self._queue.addItem(track)

    @guard
    def empty(self):
        self._queue.clear()

    @property
    @guard
    def deeplink(self):
        return BASE_URL + Config.serverId + EXT + QUEUE + str(self.id)


class RadioPlaylist(BaseQueue):
    def _initialize(self, track):
        if self._server is None:
            raise Exception("Server required")
        try:
            self._queue = self._server.playlist("HamRadio")  # TODO: configurable
        except:
            self._queue = Playlist.create(self._server, "HamRadio", items=[track])

    @property
    @guard
    def id(self):
        return self._queue.key

    @guard
    def _addToQueue(self, track):
        self._queue.addItems([track])

    @guard
    def empty(self):
        self._queue.removeItems(self._queue.items())

    @property
    @guard
    def deeplink(self):
        return BASE_URL + Config.serverId + EXT + PLAYLIST + str(self.id)
