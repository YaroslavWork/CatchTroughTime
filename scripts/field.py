import pygame.draw
import random
from scripts.UI.text import Text
from scripts.map import Map
from scripts.wall import Wall
from scripts.settings import COUNTDOWN_TIME, ACTION_TIME, SIZE, SERVER_TICK
from enum import Enum

class GameStatus(Enum):
    PREPARING = 1
    COUNTDOWN = 2
    ACTION = 3
    AFTER_ACTION = 4
    SIMULATION = 5
    RESULTS = 6


class Field:

    def __init__(self, space, player) -> None:
        self.space = space
        self.player = player
        self.map = Map(self.space)
        self.game_status = GameStatus.PREPARING
    
        self.countdown_time_in_ms = COUNTDOWN_TIME
        self.action_time_in_ms = 0
        self.server_tick_in_ms = 1000 / SERVER_TICK
        self.count_recorded_ticks = 0

        self.movement_records = []

        self.prepare_action()
       
    def prepare_action(self) -> None:
        self.game_status = GameStatus.PREPARING
        self.map.load("maps_conf/first_map.json")
        self.map.set_players(1, self.player, change_role=True)
        self.player.block_movement()

    def start_countdown(self) -> None:
        self.game_status = GameStatus.COUNTDOWN
        self.countdown = COUNTDOWN_TIME
        

    def update(self, dt: float, mouse_pos: list[float, float]) -> None:
        self.player.update(mouse_pos)

        if self.game_status == GameStatus.COUNTDOWN:
            self.countdown_time_in_ms -= dt
            if self.countdown_time_in_ms <= 0:
                self.game_status = GameStatus.ACTION
                self.action_time_in_ms = 0
                self.player.unblock_movement()
        elif self.game_status == GameStatus.ACTION:
            self.action_time_in_ms += dt

            if self.action_time_in_ms // self.server_tick_in_ms > self.count_recorded_ticks:
                self.count_recorded_ticks += 1
                self.movement_records.append(self.player.get_pos())

            if self.action_time_in_ms >= ACTION_TIME:
                self.game_status = GameStatus.AFTER_ACTION
                self.player.block_movement()

    def draw(self, screen, camera) -> None:
        self.map.draw(screen, camera)
        self.player.draw(screen, camera)


        status_game_text_pos = (SIZE[0] - 100, 20)
        color = (30, 128, 255)
        if self.game_status == GameStatus.PREPARING:
            Text("PREPARING", color, 20).print(screen, status_game_text_pos)
        elif self.game_status == GameStatus.COUNTDOWN:
            Text("COUNTDOWN", color, 20).print(screen, status_game_text_pos)
            Text(str(int(self.countdown_time_in_ms / 1000)+1), (0, 0, 255), 400).print(screen, (SIZE[0]//2, SIZE[1]//2), True)
        elif self.game_status == GameStatus.ACTION:
            Text("ACTION", color, 20).print(screen, status_game_text_pos)
            Text(str(int((ACTION_TIME - self.action_time_in_ms) / 1000)), (0, 128, 255), 30).print(screen, (SIZE[0]//2, 20), True)
        elif self.game_status == GameStatus.AFTER_ACTION:
            Text("AFTER ACTION", color, 20).print(screen, status_game_text_pos)
        elif self.game_status == GameStatus.SIMULATION:
            Text("SIMULATION", color, 20).print(screen, status_game_text_pos)
        elif self.game_status == GameStatus.RESULTS:
            Text("RESULTS", color, 20).print(screen, status_game_text_pos)

        