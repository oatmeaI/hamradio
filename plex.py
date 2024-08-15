from plexapi.server import PlexServer, Playlist, PlayQueue, PlexClient
from urllib import parse
import sys
# import rich

QUEUE_LEN = 12  # multiple of novelty value
START_DIST = 0.10
MAX_DIST = 0.7
DIST_STEP = 0.05
NOVELTY = 3  # 1 familiar & 2 new
MAX_PLAYS = 100  # TODO: this should be the max plays in the library
# TODO: load from config
PORT = ""
TOKEN = ""
SERVER = ""


class Plex:
    def __init__(self) -> None:
        self.plex = PlexServer(SERVER, TOKEN)
        self.nextUp = None
        self.queue = []

    def sortTrack(self, track):
        # Prefer higher-rated tracks with fewer plays
        # TODO: prefer less recently played
        rating = (track.userRating or 0) / 10.0
        plays = (MAX_PLAYS - (track.viewCount or 0)) / MAX_PLAYS
        return rating + plays

    def filterTrack(self, track, baseTrack, novel):
        diffAlbum = (
            track.artist().title != baseTrack.artist().title
            or track.album().title != baseTrack.album().title
        )

        if novel:
            return track not in self.queue and track.viewCount < 1 and diffAlbum
        else:
            return track not in self.queue and track.viewCount > 0 and diffAlbum

    def getNextUp(self, baseTrack, novel):
        dist = START_DIST
        filtered = []

        while len(filtered) < 1 and dist <= MAX_DIST:
            all = baseTrack.sonicallySimilar(maxDistance=dist)

            filtered = list(
                filter(
                    lambda track: self.filterTrack(track, baseTrack, novel),
                    all,
                )
            )

            filtered.sort(key=self.sortTrack, reverse=True)
            if len(filtered) < 1:
                dist = dist + DIST_STEP
                print(">>> Increasing distance to " + str(dist))

        return filtered[0]

    def getTrackFromLink(self, link):
        # TODO: gross
        trackId = parse.parse_qs(parse.urlparse(link).query)["key"][0]
        return self.plex.fetchItem(trackId)

    def makePlaylist(self):
        client = PlexClient(baseurl="http://127.0.0.1:" + PORT)

        nextUp = None
        plexQueue = None
        if len(sys.argv) > 1:
            nextUp = self.getTrackFromLink(sys.argv[1])
            self.queue.append(nextUp)
            plexQueue = self.plex.createPlayQueue(self.queue)
            client.playMedia(plexQueue)

        if client.timeline and client.timeline.key:
            nextUp = self.plex.fetchItem(client.timeline.key)
            plexQueue = PlayQueue.get(self.plex, client.timeline.playQueueID)
            self.queue.append(nextUp)

        # TODO: if already playing & current track is the same as first track, dont restart
        # TODO: shortcut to just run with current track since share isnt always available
        client.play()
        while len(self.queue) < QUEUE_LEN:
            novel = len(self.queue) % NOVELTY != 0
            nextUp = self.getNextUp(nextUp, novel)
            print(nextUp, nextUp.viewCount, novel)
            if nextUp is not None and nextUp not in self.queue:
                self.queue.append(nextUp)
                plexQueue.addItem(nextUp)
                plexQueue.refresh()
                client.refreshPlayQueue(plexQueue.playQueueID)
                print(nextUp.title)

        self.queue = []


Plex().makePlaylist()
