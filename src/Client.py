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
    def __init__(self, server, address, name=None) -> None:
        self._server = server
        try:
            print("client address", address, name)
            clients = server.clients()
            self._client = next(
                (c for c in clients if c.address == address or c.title == name), None
            )
            for c in clients:
                print("existing client:", c.address, c.title)
        except Exception as e:
            print("Client exception", e)
            self._client = None

        try:
            sessions = server.sessions()
            self._session = next(
                (
                    s
                    for s in sessions
                    if s.player.address == address or s.player.title == name
                ),
                None,
            )
            for c in sessions:
                print("existing session:", c.player.title)
        except Exception as e:
            print(e)
            self._session = None

        print("client init:", self._client, self._session)

    @property
    def connected(self):
        if self._client is None:
            return False
        try:
            self._client.connect()
            return True
        except:
            return False

    @property
    def currentQueueId(self):
        if (
            self.connected is False
            or self._client is None
            or self._client.timeline is None
        ):
            return
        return self._client.timeline.playQueueID

    @property
    def currentTrack(self):
        if (
            self.connected is True
            and self._client is not None
            and self._client.timeline is not None
        ):
            return self._server.fetchItem(self._client.timeline.key)
        if self._session is not None:
            return self._server.fetchItem(self._session.key)

    @property
    def currentTrackId(self):
        if (
            self.connected is True
            and self._client is not None
            and self._client.timeline is not None
        ):
            return self._client.timeline.key
        if self._session is not None:
            return self._session.key

    def refreshQueue(self, queue):
        if self.connected is False or self._client is None:
            return
        try:
            self._client.refreshPlayQueue(self.currentQueueId)
        except Exception as e:
            print("refreshQueue: Error contacting client", e)

    def pause(self):
        if self.connected is False or self._client is None:
            return
        self._client.pause(mtype="music")

    def play(self, queue: BaseQueue):
        print(self._client)
        if self._client is not None and self.connected is True:
            if self.currentQueueId == queue.id:
                print("Refreshing queue")
                self._client.refreshPlayQueue(queue.id)
            else:
                print("Starting queue")
                self._client.playMedia(queue._queue)
            return "Done"
        else:
            print("Sending deeplink")
            return queue.deeplink
