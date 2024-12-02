import pygame

class Map:

    def __init__(self, name: str, size: tuple[int, int], rounds: int, time: int, players_start_pos: list[tuple(float, float)], walls_pos: list[pygame.Rect]) -> None:
        self.name = name
        self.size = size
        self.rounds = rounds
        self.time = time
        self.players_start_pos = players_start_pos
        self.walls_pos = walls_pos

    def draw(self, screen, camera) -> None:
        NotImplementedError("Start coding here!")

    def update(self, dt: float) -> None:
        NotImplementedError("Start coding here!")