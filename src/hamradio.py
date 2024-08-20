import sys
from Bootstrap import bootstrap
from Tuner import Tuner


stations = bootstrap()
station = stations["new-stuff"]
tuner = Tuner(clientName="iPhone")

tuner.tuneIn(station)
