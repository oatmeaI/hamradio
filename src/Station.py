import random


class Station:
    def __init__(self, name, kinds, weights, seed=None):
        self.name = name
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
