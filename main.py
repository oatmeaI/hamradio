from plexapi.server import PlexServer, PlayQueue, PlexClient
import random
import tomllib
import time


def loadSimilar(track):
    if track is None:
        raise Exception("Need a track")
    return track.sonicallySimilar()


def loadRandom(_):
    config = Config()
    server = PlexServer(config.server, config.token)
    section = server.library.section(config.musicSection)
    return section.searchTracks(maxresults=1, sort="random")[0]


loaders = {"similar": loadSimilar, "random": loadRandom}

maxes = {
    "playcount": lambda t: 100,  # TODO: This should fetch, or be configured
    "rating": lambda t: 10,
    "lastplay": lambda t: time.time(),
}

getters = {
    "playcount": lambda t: t.viewCount,
    "rating": lambda t: t.userRating,
    "lastplay": lambda t: t.lastViewedAt.timestamp(),
}


def stat(stat, track):
    return getters[stat](track) or 0


def statMax(stat, track):
    return maxes[stat](track)


class Filter:
    def __init__(self, key, operator, value):
        self.key = key
        self.operator = operator
        self.value = value

    def filterTrack(self, track):
        val = stat(self.key, track)
        if self.operator == "<":
            return val < self.value
        if self.operator == ">":
            return val > self.value

    def filter(self, tracks):
        return list(filter(lambda track: self.filterTrack(track), tracks))


class Sort:
    def __init__(self, key, weight):
        self.key = key
        self.weight = weight

    def calc(self, track):
        val = stat(self.key, track)
        max = statMax(self.key, track)
        return (val / max) * self.weight


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
        filtered = list(
            filter(
                lambda t: t.parentTitle + t.grandparentTitle not in queue.albums,
                options,
            )
        )
        filtered = self.filter(filtered)
        sorted = self.sort(filtered)

        if len(sorted) > 0:
            return sorted[0]


class Station:
    def __init__(self, kinds, weights, seed=None):
        self.kinds = kinds
        self.weights = weights
        self.seed = seed

    def selectNextSource(self):
        return random.choices(self.kinds, weights=self.weights)[0]

    # pass queue here to filter out tracks already in queue. feels messy
    def getTrack(self, queue):
        source = self.selectNextSource()
        print(source.name)
        return source.getTrack(queue)


class Queue:
    tracks = []
    albums = []

    def __init__(self, server, client) -> None:
        self.server = server
        self.client = client
        self._queue = None
        if client.currentQueueId:
            currentTrack = server.fetchItem(client.currentTrackId)
            self._queue = PlayQueue.get(server, client.currentQueueId)
            self.tracks.append(currentTrack)
            self.empty()
        elif client.currentTrackId:
            currentTrack = server.fetchItem(client.currentTrackId)
            self._queue = PlayQueue.create(server, [currentTrack])
            self.tracks.append(currentTrack)
            self.empty()

    def _initialize(self, track):
        self._queue = PlayQueue.create(self.server, [track])
        self.client.play(self._queue)

    @property
    def id(self):
        if self._queue is not None:
            return self._queue.playQueueID

    @property
    def length(self):
        return len(self.tracks)

    def addTrack(self, track):
        print(self._queue)
        if self._queue is None:
            self._initialize((track))
        else:
            self._queue.refresh()
            self._queue.addItem(track)
        self.tracks.append(track)
        self.albums.append(track.parentTitle + track.grandparentTitle)

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
            self.musicSection = data["musicSection"]


config = Config()


class Client:
    def __init__(self, server) -> None:
        self._server = server
        self._client = PlexClient(
            baseurl=config.clientAddress + ":" + config.clientPort
        )

    @property
    def currentQueueId(self):
        try:
            return self._client.timeline.playQueueID
        except Exception as e:
            print("currentQueueId: Error contacting client", e)

    @property
    def currentTrackId(self):
        try:
            return self._client.timeline.key
        except Exception as e:
            print("currentTrackId: Error contacting client", e)

    def refreshQueue(self, queue):
        try:
            self._client.refreshPlayQueue(self.currentQueueId)
        except Exception as e:
            print("refreshQueue: Error contacting client", e)

    def play(self, queue=None):
        try:
            if queue:
                self._client.playMedia(queue)
            else:
                self._client.play()
        except Exception as e:
            print("play: Error contacting client", e)


class Tuner:
    def tuneIn(self, station):
        config = Config()
        server = PlexServer(config.server, config.token)
        client = Client(server)
        # print(config.clientAddress, config.clientPort)
        queue = Queue(server, client)

        if len(queue.tracks) < 1 and station.seed:
            print("seeding")
            seeded = station.seed.getTrack(queue)
            print(seeded)
            queue.addTrack(seeded)

        client.play()

        while queue.length < config.queueLength:
            nextUp = station.getTrack(queue)
            queue.addTrack(nextUp)
            client.refreshQueue(queue)
            print(nextUp)


def buildSource(sourceConfig):
    filters = [
        Filter(f["key"], f["operator"], f["value"]) for f in sourceConfig["filters"]
    ]
    sorts = [Sort(s["key"], s["weight"]) for s in sourceConfig["sorts"]]
    loader = loaders[sourceConfig["loader"]]
    return Source(loader, filters, sorts, sourceConfig["name"])


with open("stations.toml", "rb") as f:
    data = tomllib.load(f)
    sources = {}
    stations = []

    for sourceConfig in data["sources"]:
        sources[sourceConfig["name"]] = buildSource(sourceConfig)
        # filters = [
        #     Filter(f["key"], f["operator"], f["value"]) for f in sourceConfig["filters"]
        # ]
        # sorts = [Sort(s["key"], s["weight"]) for s in sourceConfig["sorts"]]
        # loader = loaders[sourceConfig["loader"]]
        # sources[sourceConfig["name"]] = Source(
        #     loader, filters, sorts, sourceConfig["name"]
        # )

    for stationConfig in data["stations"]:
        _sources = [sources[s["source"]] for s in stationConfig["sources"]]
        weights = [s["weight"] for s in stationConfig["sources"]]
        seed = sources[stationConfig["seed"]] if "seed" in stationConfig else None
        station = Station(_sources, weights, seed)
        stations.append(station)

    r = Tuner()
    r.tuneIn(stations[0])
