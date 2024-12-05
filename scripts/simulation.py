import pygame

from scripts.UI.text import Text
from scripts.map import Map
from scripts.player import PlayerRole
from scripts.settings import PLAYER_RADIUS, COLORS

class Simulation:

    def __init__(self, players_names: list[str], players_roles: list[PlayerRole], players_pos: list[list[float, float]], map: Map, server_ticks: int = 20) -> None:
        self.players_names = players_names
        self.players_roles = players_roles
        self.players_pos = players_pos
        self.map = map
        self.server_ticks_in_ms = 1000 / server_ticks
        self.current_players_position = [(0, 0) for _ in range(len(players_names))]

        self.simulation_time_in_ms = 0
        self.is_paused = True
        self.collision_is_detected = False

    def start(self) -> None:
        self.is_paused = False

    def stop(self) -> None:
        self.is_paused = True

    def move_to(self, time_in_ms: int) -> None:
        self.simulation_time_in_ms = time_in_ms
        self.set_current_positions(self.simulation_time_in_ms)

    def set_current_positions(self, time_in_ms: int) -> None:
        current_tick = int(time_in_ms // self.server_ticks_in_ms)
        progress = (time_in_ms % self.server_ticks_in_ms) / self.server_ticks_in_ms
        # Linear interpolation
        if current_tick + 1 >= len(self.players_pos[0]):
            return
        
        for i, player_pos in enumerate(self.players_pos):
            x = player_pos[current_tick][0] + (player_pos[current_tick + 1][0] - player_pos[current_tick][0]) * progress
            y = player_pos[current_tick][1] + (player_pos[current_tick + 1][1] - player_pos[current_tick][1]) * progress
            self.current_players_position[i] = (x, y)

    def check_collision_between_catcher_and_runner(self) -> None:
        for i in range(len(self.current_players_position)):
            for j in range(len(self.current_players_position)):
                if i == j:
                    continue

                x1, y1 = self.current_players_position[i]
                x2, y2 = self.current_players_position[j]

                if (x1 - x2) ** 2 + (y1 - y2) ** 2 <= 4 * PLAYER_RADIUS ** 2:
                    if self.players_roles[i] == PlayerRole.RUNNER and self.players_roles[j] == PlayerRole.CATCHER or\
                        self.players_roles[i] == PlayerRole.CATCHER and self.players_roles[j] == PlayerRole.RUNNER:
                        self.collision_is_detected = True
                        return

    def get_time(self) -> int:
        return self.simulation_time_in_ms

    def update(self, dt: float) -> None:
        if not self.is_paused:
            self.simulation_time_in_ms += dt
            self.set_current_positions(self.simulation_time_in_ms)
            self.check_collision_between_catcher_and_runner()

    def draw(self, screen, camera):
        self.map.draw(screen, camera)
        for i, player_pos in enumerate(self.current_players_position):
            x, y = camera.get_local_point(player_pos[0], player_pos[1])
            r = camera.get_local_radius(PLAYER_RADIUS)
            if self.players_roles[i] == PlayerRole.CATCHER:
                pygame.draw.circle(screen, COLORS['catcher'], (x, y), r)
            else:
                pygame.draw.circle(screen, COLORS['runner'], (x, y), r)
            Text(self.players_names[i], (0, 0, 0), 14).print(screen, (x+20, y-40))