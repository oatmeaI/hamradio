import webbrowser
from Config import Config
from plexapi.server import PlexClient
from Queue import BaseQueue


def guard(fn):
    def wrapped(self):
        if self._client.timeline is None:
            return
        fn(self)

    return wrapped


class Client:
    def __init__(self, server) -> None:
        self._server = server
        try:
            self._client = PlexClient(
                baseurl=Config.clientAddress + ":" + Config.clientPort
            )
        except:
            self._client = None

    @property
    def connected(self):
        try:
            self._client.connect()
            return True
        except:
            return False

    @property
    def currentQueueId(self):
        if self.connected is False:
            return
        if self._client.timeline is None:
            return
        return self._client.timeline.playQueueID

    @property
    def currentTrackId(self):
        if self.connected is False:
            return
        if self._client.timeline is None:
            return
        return self._client.timeline.key

    def refreshQueue(self, queue):
        if self.connected is False:
            return
        try:
            self._client.refreshPlayQueue(self.currentQueueId)
        except Exception as e:
            print("refreshQueue: Error contacting client", e)

    def pause(self):
        if self.connected is False:
            return
        self._client.pause(mtype="music")

    def play(self, queue: BaseQueue):
        if self.connected:
            print(queue._queue)
            self._client.playMedia(queue._queue)
            return "Done"
        else:
            return queue.deeplink
