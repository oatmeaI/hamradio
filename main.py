from plexapi.server import PlexServer, PlayQueue, PlexClient
import random

# TODO: load configs from file
# TODO: load station config from file
# TODO: exclude already added tracks from queue
# TODO: more operators in filters
# TODO: weights for different Kinds
# TODO: more sources


class Source:
    def load(self, track):
        pass


class SimilarSource(Source):
    def load(self, track):
        return track.sonicallySimilar()


class Filter:
    def __init__(self, key, operator, value):
        self.key = key
        self.operator = operator
        self.value = value

    def filterTrack(self, track):
        # TODO: better way to do this?
        if self.operator == "<":
            return getattr(track, self.key) < self.value
        if self.operator == ">":
            return getattr(track, self.key) > self.value

    def filter(self, tracks):
        return list(filter(lambda track: self.filterTrack(track), tracks))


class Sort:
    def __init__(self, key, weight, max):
        self.key = key
        self.weight = weight
        self.max = max

    def calc(self, track):
        attr = getattr(track, self.key) or 0
        return (attr / self.max) * self.weight


# TODO: better name
class Kind:
    def __init__(self, source, filters, sorts, weight):
        self.source = source
        self.filters = filters
        self.sorts = sorts
        self.weight = weight

    def filter(self, tracks):
        tracks = tracks
        for filter in self.filters:
            tracks = filter.filter(tracks)
        return tracks

    def calcSort(self, track):
        score = 0.0
        for sort in self.sorts:
            score = score + sort.calc(track)
        return score

    def sort(self, tracks):
        return sorted(tracks, key=self.calcSort, reverse=True)

    def getTrack(self, queue):
        options = self.source.load(queue.tracks[-1])
        filtered = self.filter(options)
        sorted = self.sort(filtered)

        if len(sorted) > 0:
            return sorted[0]


class Station:
    def __init__(self, kinds):
        self.kinds = kinds

    def selectNextKind(self):
        # TODO: Weight
        return random.choice(self.kinds)

    # pass queue here to filter out tracks already in queue. feels messy
    def getTrack(self, queue):
        kind = self.selectNextKind()
        return kind.getTrack(queue)


class Queue:
    tracks = []

    def __init__(self, server, client) -> None:
        self._queue = PlayQueue.get(server, client.currentQueueId)
        currentTrack = server.fetchItem(client.currentTrackId)
        self.tracks.append(currentTrack)

    @property
    def id(self):
        return self._queue.playQueueID

    @property
    def length(self):
        return len(self.tracks)

    def addTrack(self, track):
        self.tracks.append(track)
        self._queue.addItem(track)
        self._queue.refresh()


class Config:
    queueLength = 10
    port = ""
    server = ""
    token = ""


config = Config()


class Client:
    def __init__(self, server) -> None:
        self._server = server
        self._client = PlexClient(baseurl="http://127.0.0.1:" + config.port)

    @property
    def currentQueueId(self):
        return self._client.timeline.playQueueID

    @property
    def currentTrackId(self):
        return self._client.timeline.key

    def refreshQueue(self, queue):
        self._client.refreshPlayQueue(self.currentQueueId)

    def play(self):
        self._client.play()


class Radio:
    def create(self, station):
        config = Config()
        server = PlexServer(config.server, config.token)
        client = Client(server)
        queue = Queue(server, client)

        client.play()

        while queue.length < config.queueLength:
            nextUp = station.getTrack(queue)
            queue.addTrack(nextUp)
            client.refreshQueue(queue)


likedSort = Sort(key="userRating", weight=1, max=10)
playedFilter = Filter(key="viewCount", operator=">", value=0)
unplayedFilter = Filter(key="viewCount", operator="<", value=1)
played = Kind(
    source=SimilarSource(), filters=[playedFilter], sorts=[likedSort], weight=0.5
)
unplayed = Kind(source=SimilarSource(), filters=[unplayedFilter], sorts=[], weight=0.5)
s = Station([played, unplayed])
r = Radio()
r.create(s)
