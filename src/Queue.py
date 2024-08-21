from typing import Optional
from plexapi.server import PlayQueue, Playlist
from plexapi.audio import Track

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

    def __init__(self, server, client):
        self._server = server
        self.client = client

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
            self.logTrack(track)

    def logTrack(self, track):
        self.tracks.append(track)
        self.albums.append(track.parentTitle + track.grandparentTitle)

    def empty(self):
        pass

    @property
    def deeplink(self):
        return ""


class Queue(BaseQueue):
    def __init__(self, server, client):
        self._server = server
        self.client = client
        self.tracks = []
        self.albums = []

        # TODO: clean up this vs _initialize
        if self.client.currentQueueId:
            self._queue = PlayQueue.get(self._server, self.client.currentQueueId)
            self.empty()

        if self.client.currentTrack:
            self.logTrack(self.client.currentTrack)

    def initializeFromExisting(self, track):
        if self._server is None:
            return

        self._queue = PlayQueue.get(self._server, self.client.currentQueueId)

        # TODO: Log all tracks already in queue
        # TODO: add option to clear all tracks in queue except for current
        self.empty()

        self._addToQueue(track)
        self.logTrack(track)

        currentTrack = self.client.currentTrack
        self.logTrack(currentTrack)

    def initializeFromScratch(self, track):
        if self._server is None:
            return

        if self.client.currentTrackId:
            currentTrack = self.client.currentTrack

            self.logTrack(currentTrack)
            self.logTrack(track)

            self._queue = PlayQueue.create(self._server, [currentTrack, track])
        else:
            self._queue = PlayQueue.create(self._server, [track])
            self.logTrack(track)

    def _initialize(self, track):
        if self._server is None:
            return
        if self.client.currentQueueId:
            self.initializeFromExisting(track)
        else:
            self.initializeFromScratch(track)

        print("Queue initialized with:", self.tracks)

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
