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
