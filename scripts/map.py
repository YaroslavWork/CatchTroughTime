import pygame
import json

from scripts.player import Player, PlayerRole
from scripts.wall import Wall
from scripts.settings import COLORS, PLAYER_RADIUS

class Map:

    def __init__(self, space) -> None:
        self.space = space

        self.name = None
        self.rounds = None
        self.time = None
        self.size = None
        self.catcher_start_pos = None
        self.walls = None

    def load(self, path: str) -> None:
        with open(path, "r") as file:
            data = json.load(file)
            self.name = data["name"]
            self.rounds = data["rounds"]
            self.time = data["time"]
            self.size = data["map_size"]["width"], data["map_size"]["height"]
            self.catcher_start_pos = data["catcher_start_pos"]
            self.runner_start_pos = data["runner_start_pos"]

            walls_pos = data["walls"]
            self.walls = []
            for wall_pos in walls_pos:
                x = wall_pos["pos"]["x"]
                y = wall_pos["pos"]["y"]
                w = wall_pos["size"]["width"]
                h = wall_pos["size"]["height"]
                self.walls.append(Wall(pygame.Rect(x, y, w, h)))
                self.walls[-1].create_rectangle(self.space)

    def set_players(self, start_id: int, player, change_role=False) -> None:
        # STARTS FROM CATHERS
        if start_id < len(self.catcher_start_pos):
            player.set_pos(self.catcher_start_pos[start_id]["x"], self.catcher_start_pos[start_id]["y"])
            if change_role:
                player.role = PlayerRole.CATCHER
        else:
            player.set_pos(self.runner_start_pos[start_id - len(self.catcher_start_pos)]["x"], self.runner_start_pos[start_id - len(self.catcher_start_pos)]["y"])
            if change_role:
                player.role = PlayerRole.RUNNER

    def draw(self, screen, camera) -> None:
        for wall in self.walls:
            wall.draw(screen, camera)

        # Draw borders
        local_pos_lefttop = camera.get_local_point(0, 0)
        local_pos_rightbottom = camera.get_local_point(self.size[0], self.size[1])
        pygame.draw.rect(screen, (255, 128, 0), (local_pos_lefttop[0], local_pos_lefttop[1], local_pos_rightbottom[0] - local_pos_lefttop[0], local_pos_rightbottom[1] - local_pos_lefttop[1]), 2)

        # Draw start positions
        local_radius = camera.get_local_radius(PLAYER_RADIUS)
        for runner in self.runner_start_pos:
            pygame.draw.circle(screen, COLORS["runner"], camera.get_local_point(runner["x"], runner["y"]), local_radius, 2)
        for catcher in self.catcher_start_pos:
            pygame.draw.circle(screen, COLORS["catcher"], camera.get_local_point(catcher["x"], catcher["y"]), local_radius, 2)



    def update(self, dt: float) -> None:
        NotImplementedError("Start coding here!")