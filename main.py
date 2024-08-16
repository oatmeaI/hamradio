from plexapi.server import PlexServer, PlayQueue, PlexClient
import random
import tomllib


class Filter:
    def __init__(self, key, operator, value):
        self.key = key
        self.operator = operator
        self.value = value

    def filterTrack(self, track):
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


class Source:
    def __init__(self, loader, filters, sorts, name):
        self.loader = loader
        self.filters = filters
        self.sorts = sorts
        self.name = name

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
        currentTrack = queue.tracks[-1] if len(queue.tracks) > 0 else None
        options = self.loader(currentTrack)
        filtered = list(filter(lambda t: t not in queue.tracks, options))
        filtered = self.filter(filtered)
        sorted = self.sort(filtered)

        if len(sorted) > 0:
            return sorted[0]


class Station:
    def __init__(self, kinds, weights):
        self.kinds = kinds
        self.weights = weights

    def selectNextSource(self):
        return random.choices(self.kinds, weights=self.weights)[0]

    # pass queue here to filter out tracks already in queue. feels messy
    def getTrack(self, queue):
        source = self.selectNextSource()
        print(source.name)
        return source.getTrack(queue)


class Queue:
    tracks = []

    def __init__(self, server, client) -> None:
        self.server = server
        self._queue = None
        if client.currentQueueId:
            currentTrack = server.fetchItem(client.currentTrackId)
            self._queue = PlayQueue.get(server, client.currentQueueId)
            self.tracks.append(currentTrack)
        elif client.currentTrackId:
            currentTrack = server.fetchItem(client.currentTrackId)
            self._queue = PlayQueue.create(server, [currentTrack])
            self.tracks.append(currentTrack)

    @property
    def id(self):
        if self._queue is not None:
            return self._queue.playQueueID

    @property
    def length(self):
        return len(self.tracks)

    def addTrack(self, track):
        if self._queue is None:
            self._queue = PlayQueue.create(self.server, [track])
        else:
            self._queue.refresh()
            self._queue.addItem(track)
        self.tracks.append(track)

    def empty(self):
        if self._queue is not None:
            self._queue.clear()


class Config:
    def __init__(self):
        with open("config.toml", "rb") as f:
            data = tomllib.load(f)
            self.queueLength = data["queueLength"] if "queueLength" in data else 10
            self.clientAddress = (
                data["clientAddress"] if "clientAddress" in data else "http://127.0.0.1"
            )
            self.clientPort = data["clientPort"] if "clientPort" in data else "32500"
            self.server = data["server"]
            self.token = data["token"]


config = Config()


class Client:
    def __init__(self, server) -> None:
        self._server = server
        self._client = PlexClient(baseurl="http://127.0.0.1:" + config.clientPort)

    @property
    def currentQueueId(self):
        try:
            return self._client.timeline.playQueueID
        except:
            print("Error contacting client")

    @property
    def currentTrackId(self):
        try:
            return self._client.timeline.key
        except:
            print("Error contacting client")

    def refreshQueue(self, queue):
        try:
            self._client.refreshPlayQueue(self.currentQueueId)
        except:
            print("Error contacting client")

    def play(self):
        try:
            self._client.play()
        except:
            print("Error contacting client")


class Tuner:
    def tuneIn(self, station):
        config = Config()
        server = PlexServer(config.server, config.token)
        client = Client(server)
        queue = Queue(server, client)

        queue.empty()
        client.play()

        while queue.length < config.queueLength:
            nextUp = station.getTrack(queue)
            queue.addTrack(nextUp)
            client.refreshQueue(queue)
            print(nextUp)


def loadSimilar(track):
    if track is None:
        raise Exception("Need a track")
    return track.sonicallySimilar()


loaders = {"similar": loadSimilar}

with open("stations.toml", "rb") as f:
    data = tomllib.load(f)
    sources = {}
    stations = []

    for sourceConfig in data["sources"]:
        filters = [
            Filter(f["key"], f["operator"], f["value"]) for f in sourceConfig["filters"]
        ]
        sorts = [Sort(s["key"], s["weight"], s["max"]) for s in sourceConfig["sorts"]]
        loader = loaders[sourceConfig["loader"]]
        sources[sourceConfig["name"]] = Source(
            loader, filters, sorts, sourceConfig["name"]
        )

    for stationConfig in data["stations"]:
        sources = [sources[s["source"]] for s in stationConfig["sources"]]
        weights = [s["weight"] for s in stationConfig["sources"]]
        station = Station(sources, weights)
        stations.append(station)

    r = Tuner()
    r.tuneIn(stations[0])


# likedSort = Sort(key="userRating", weight=1, max=10)
# playedFilter = Filter(key="viewCount", operator=">", value=0)
# unplayedFilter = Filter(key="viewCount", operator="<", value=1)
# played = Source(
#     loader=LoadSimilar(), filters=[playedFilter], sorts=[likedSort], weight=0.5
# )
# unplayed = Source(loader=LoadSimilar(), filters=[unplayedFilter], sorts=[], weight=0.5)
# s = Station([played, unplayed])
# r.create(s)
