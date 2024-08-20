try:
    import tomllib
except:
    import tomli as tomllib


class _Config:
    def __init__(self):
        with open("../config.toml", "rb") as f:
            data = tomllib.load(f)
            self.queueLength = data["queueLength"] if "queueLength" in data else 10
            self.clientAddress = (
                data["clientAddress"] if "clientAddress" in data else "http://127.0.0.1"
            )
            self.clientPort = data["clientPort"] if "clientPort" in data else "32500"
            self.server = data["server"]
            self.token = data["token"]
            self.musicSection = data["musicSection"]
            self.serverId = data["serverId"]


Config = _Config()
