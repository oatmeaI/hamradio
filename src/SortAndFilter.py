from stats import Stat


class Filter:
    def __init__(self, key, operator, value):
        self.key = key
        self.operator = operator
        self.value = value

    def filterTrack(self, track):
        val = Stat(self.key, track).val()

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
        stat = Stat(self.key, track)
        val = stat.val()
        max = stat.max()
        return (val / max) * self.weight
