from komora_syncer.connections.NetboxConnection import NetboxConnection

class NetboxBase:
    def __init__(self):
        self.nb = NetboxConnection.get_connection()