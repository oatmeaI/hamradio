try:
    import tomllib
except:
    import tomli as tomllib

from Source import Source
from Station import Station
from loaders import Loaders
from SortAndFilter import Filter, Sort


def buildSource(sourceConfig):
    filters = [
        Filter(f["key"], f["operator"], f["value"]) for f in sourceConfig["filters"]
    ]
    sorts = [Sort(s["key"], s["weight"]) for s in sourceConfig["sorts"]]
    loader = Loaders[sourceConfig["loader"]]
    return Source(loader, filters, sorts, sourceConfig["name"])


def bootstrap():
    with open("../stations.toml", "rb") as f:
        data = tomllib.load(f)
        sources = {}
        stations = {}

        for sourceConfig in data["sources"]:
            sources[sourceConfig["name"]] = buildSource(sourceConfig)

        for stationConfig in data["stations"]:
            _sources = [sources[s["source"]] for s in stationConfig["sources"]]
            weights = [s["weight"] for s in stationConfig["sources"]]
            seed = sources[stationConfig["seed"]] if "seed" in stationConfig else None
            station = Station(stationConfig["name"], _sources, weights, seed)
            stations[stationConfig["name"]] = station

    return stations
