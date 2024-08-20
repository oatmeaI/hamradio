import time
import random

maxes = {
    "playcount": lambda t: 100,  # TODO: This should fetch, or be configured
    "rating": lambda t: 10,
    "lastplay": lambda t: time.time(),  # TODO: fix scale here; minimum isn't 0
    "random": lambda t: 1,
}

getters = {
    "playcount": lambda t: t.viewCount,
    "rating": lambda t: t.userRating,
    "lastplay": lambda t: t.lastViewedAt.timestamp(),
    "random": lambda t: random.random(),
}


class Stat:
    def __init__(self, name, track):
        self.name = name
        self.track = track

    def val(self):
        return getters[self.name](self.track) or 0

    def max(self):
        return maxes[self.name](self.track)
