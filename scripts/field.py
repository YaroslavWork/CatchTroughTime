import pygame.draw


class Field:

    def __init__(self) -> None:
        NotImplementedError("Start coding here!")

    def update(self, dt: float) -> None:
        NotImplementedError("Start coding here!")

    def draw(self, screen, camera) -> None:
        NotImplementedError("Start coding here!")