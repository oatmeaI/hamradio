from flask import Flask, request
from Bootstrap import bootstrap
from Tuner import Tuner

app = Flask(__name__)


@app.route("/")
def hamRadio():
    clientAddr = request.remote_addr
    clientName = request.args.get("client")
    stationName = request.args.get("station")
    stations = bootstrap()
    station = stations[stationName]
    tuner = Tuner(clientAddr=clientAddr, clientName=clientName)
    return tuner.tuneIn(station) or "Done"


@app.route("/stations")
def stations():
    stations = bootstrap()
    return [s for s in stations]
