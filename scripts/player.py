import enum


class PlayerRole(enum):
    CATCHER = 1
    RUNNER = 2


class Player:

    def __init__(self, uuid: str, name: str, role: PlayerRole) -> None:
        self.uuid = uuid
        self.name = name
        self.role = role