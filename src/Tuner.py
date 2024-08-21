from enum import Enum
from Client import Client
from Config import Config
from Queue import Queue, RadioPlaylist
from Server import server

# NOTE: class properties prefixed with `_` generally indicate a PlexApi object (vs a HamRadio object)


class Mode(Enum):
    fresh = 1  # Ignore currently playing track
    flow = 2  # Start with currently playing track


class Output(Enum):
    playqueue = 1  # Create a transient playqueue
    playlist = 2  # Create a playlist


class Tuner:
    def __init__(
        self, clientAddr=None, clientName=None, mode=Mode.flow, output=Output.playqueue
    ):
        self.mode = mode
        self.clientAddr = clientAddr
        self.clientName = clientName
        self.output = output
        self.server = server()

    def tuneIn(self, station):
        config = Config
        server = self.server
        client = Client(server, self.clientAddr, name=self.clientName)
        queue = (
            RadioPlaylist(server, client)
            if self.output == Output.playlist
            else Queue(server, client)
        )

        if queue.length < 1 and station.seed:
            seeded = station.seed.getTrack(queue)
            queue.addTrack(seeded)

        print("q len", queue.length)
        print(queue.tracks)

        while queue.length <= config.queueLength:
            nextUp = station.getTrack(queue)
            if nextUp is None:
                print("No more tracks")
                break
            queue.addTrack(nextUp)
            client.refreshQueue(queue)
            print(nextUp)
            print("")  # Newline

        return client.play(queue)
