class ServerPlayer:
    def __init__(self, name='', uuid='', client=None):
        self.name = name
        self.uuid = uuid
        self.client = client
        self.is_ready = False
        self.movement = []