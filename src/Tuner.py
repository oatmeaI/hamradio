from enum import Enum
from Client import Client
from Config import Config
from Queue import Queue, RadioPlaylist
from Server import server


class Mode(Enum):
    fresh = 1  # Ignore currently playing track
    flow = 2  # Start with currently playing track


class Output(Enum):
    playqueue = 1  # Create a transient playqueue
    playlist = 2  # Create a playlist


class Tuner:
    def __init__(self, clientName=None, mode=Mode.flow, output=Output.playqueue):
        self.mode = mode
        self.clientName = clientName
        self.output = output
        self.server = server()

    def createQueue(self, key):
        if self.output == Output.playlist:
            return RadioPlaylist(self.server)
        else:
            return Queue(self.server, key)

    def initQueue(self, queue):
        if self.clientName and self.mode == Mode.flow:
            session = next(
                (
                    s
                    for s in self.server.sessions()
                    if s and s.player.title == self.clientName
                ),
                None,
            )
            if session:
                track = self.server.fetchItem(session.key)
                queue.addTrack(track)

    def tuneIn(self, station):
        config = Config
        server = self.server
        client = Client(server)
        queue = self.createQueue(client.currentQueueId)

        self.initQueue(queue)

        if queue.length < 1 and station.seed:
            seeded = station.seed.getTrack(queue)
            queue.addTrack(seeded)

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
