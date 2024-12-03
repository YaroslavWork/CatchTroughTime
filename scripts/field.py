import pygame.draw
import random
from scripts.wall import Wall


class Field:

    def __init__(self, space) -> None:
        self.space = space
        self.walls = []
        for _ in range(10):
            x = random.randint(0, 1800)
            y = random.randint(0, 1600)
            w = random.randint(50, 100)
            h = random.randint(50, 100)
            self.walls.append(Wall(pygame.Rect(x, y, w, h)))
            self.walls[-1].create_rectangle(self.space)

    def update(self, dt: float) -> None:
        NotImplementedError("Start coding here!")

    def draw(self, screen, camera) -> None:
        for wall in self.walls:
            wall.draw(screen, camera)