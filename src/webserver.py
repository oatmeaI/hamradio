from flask import Flask, request
from Bootstrap import bootstrap
from Tuner import Tuner

# TODO: start from seed (should be able to get whatever is playing on named client and use that - don't add that track to playlist though)
# TODO: can we set add a track to a playqueue at a certain point
# TODO: maybe something we can do where we remote control the client on THIS machine, but then send the playqueue to the phone??
# TODO: don't restart current song in queue in remote control mode
# TODO: pass length, client address in request params

app = Flask(__name__)


@app.route("/")
def hamRadio():
    clientName = request.args.get("client")
    stationName = request.args.get("station")
    stations = bootstrap()
    station = stations[stationName]
    tuner = Tuner(clientName=clientName)
    return tuner.tuneIn(station) or "Done"


@app.route("/stations")
def stations():
    stations = bootstrap()
    return [s for s in stations]
