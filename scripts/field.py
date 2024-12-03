import pygame.draw
import random
from scripts.UI.text import Text
from scripts.map import Map
from scripts.wall import Wall


class Field:

    def __init__(self, space, player) -> None:
        self.space = space
        self.player = player
        self.map = Map(self.space)
        self.map.load("maps_conf/first_map.json")
        self.map.set_players(1, self.player, change_role=True)

    def update(self, dt: float) -> None:
        NotImplementedError("Start coding here!")

    def draw(self, screen, camera) -> None:
        self.map.draw(screen, camera)

        