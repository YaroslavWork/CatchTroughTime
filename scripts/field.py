import socket
import pygame.draw
import random
import threading
from scripts.UI.text import Text
from scripts.map import Map
from scripts.player import PlayerRole
from scripts.simulation import Simulation
from scripts.wall import Wall
from scripts.settings import COUNTDOWN_TIME, ACTION_TIME, SIZE, SERVER_TICK, COLORS
from server.transfer_messages import send_message, receive_message
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
        self.other_players = []
        self.map = Map(self.space)
        self.game_status = GameStatus.PREPARING
    
        self.countdown_time_in_ms = COUNTDOWN_TIME
        self.action_time_in_ms = 0
        self.server_tick_in_ms = 1000 / SERVER_TICK
        self.count_recorded_ticks = 0

        self.movement_records = []
        self.simulation = None
        self.winner = None

        self.sock = None
        self.server_auth_verified = False
        self.texts = ["...", "...", "...", "..."]
        self.points = [0, 0, 0, 0]

        self.connect_thread = None
        self.prepare_action()
    
    def connect_to_server(self) -> None:
        self.server_auth_verified = False
        self.texts = ["...", "...", "...", "..."]
        self.points = [0, 0, 0, 0]
        self.other_players = []
        if self.sock is not None:
            self.sock.close()
            self.sock = None
        self.connect_thread = threading.Thread(target=self.connect).start()

    def prepare_action(self) -> None:
        self.game_status = GameStatus.PREPARING
        self.map.load("conf/first_map.json")
        self.map.set_players(1, self.player, change_role=True)
        self.player.block_movement()

    def start_countdown(self) -> None:
        self.game_status = GameStatus.COUNTDOWN
        self.countdown = COUNTDOWN_TIME

    def launch_simulation(self) -> None:
        if self.game_status == GameStatus.AFTER_ACTION:
            self.game_status = GameStatus.SIMULATION
            self.simulation = Simulation(["Player"], [self.player.role], [self.movement_records], self.map, SERVER_TICK)
            self.simulation.start()

    # --- Server part ---
    def connect(self) -> None:
        self.texts[0] = "Connecting to the server..."
        self.points[0] = 1
        with open('./conf/server.txt', 'r') as file:
            data = file.read().split('\n')
            ip = data[0]
            port = int(data[1])
            password = data[2]

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, int(port)))
        except ConnectionRefusedError:
            self.texts[0] = "Connection refused"
            self.points[0] = 2
            return
        except TimeoutError:
            self.texts[0] = "Connection timeout"
            self.points[0] = 2
            return
        except socket.gaierror:
            self.texts[0] = "Wrong IP or port"
            self.points[0] = 2
            return
        except ValueError:
            self.texts[0] = "Wrong port"
            self.points[0] = 2
            return
        
        self.texts[0] = f"Connected ({ip}:{port})"
        self.points[0] = 3
        self.texts[1] = "Authenticating..."
        self.points[1] = 1

        send_message(self.sock, "auth", "connect")
        while True:
            msgs = receive_message(self.sock, 1024)
            for msg in msgs:
                if msg["type"] == "auth":
                    match msg["action"]:
                        case "request_password":
                            send_message(self.sock, "auth", "response_password", password)
                        case "request_name":
                            send_message(self.sock, "auth", "response_name", self.player.name)
                        case "success_password":
                            self.texts[1] = "Password is correct"
                            self.points[1] = 3
                            self.texts[2] = "Name is being checked..."
                            self.points[2] = 1
                        case "wrong_password":
                            self.texts[1] = "Wrong password"
                            self.points[1] = 2
                            return
                        case "field_full":
                            self.texts[1] = "Field is full"
                            self.points[1] = 2
                            return
                        case "name_taken":
                            self.texts[2] = "Name is already taken"
                            self.points[2] = 2
                            return
                        case "success_name":
                            self.texts[2] = f"Name is unique: ({self.player.name})"
                            self.points[2] = 3
                            self.texts[3] = "UUID is being provided..."
                            self.points[3] = 1
                        case "uuid":
                            self.player.uuid = msg["parameters"]
                            self.texts[3] = f"UUID is provided: ({self.player.uuid})"
                            self.points[3] = 3
                        case "success":
                            print("Auth success")
                            self.server_auth_verified = True
                elif msg["type"] == "game":
                    match msg["action"]:
                        case "new_player":
                            data = msg["parameters"]
                            uuid = data.split(" ")[0]
                            name = "".join(data.split(" ")[1:])
                            self.other_players.append({"uuid": uuid, "name": name})
        

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
        elif self.game_status == GameStatus.SIMULATION:
            self.simulation.update(dt)
            if self.simulation.get_time() >= ACTION_TIME:
                self.game_status = GameStatus.RESULTS
                self.winner = PlayerRole.RUNNER
            if self.simulation.collision_is_detected:
                self.game_status = GameStatus.RESULTS
                self.winner = PlayerRole.CATCHER

    def draw(self, screen, camera) -> None:
        if self.game_status != GameStatus.SIMULATION and self.game_status != GameStatus.RESULTS:
            self.map.draw(screen, camera)
            self.player.draw(screen, camera)
        else:
            self.simulation.draw(screen, camera)

        status_game_text_pos = (SIZE[0] - 100, 20)
        color = (30, 128, 255)
        if self.game_status == GameStatus.PREPARING:
            Text("PREPARING", color, 20).print(screen, status_game_text_pos)
            pygame.draw.rect(screen, (255, 255, 255), (SIZE[0]//2-250, SIZE[1]//2-250, 500, 400))
            if self.server_auth_verified is False:
                Text(self.texts[0], (0, 0, 0), 20).print(screen, (SIZE[0]//2-200, SIZE[1]//2-200), False)
                Text(self.texts[1], (0, 0, 0), 20).print(screen, (SIZE[0]//2-200, SIZE[1]//2-150), False)
                Text(self.texts[2], (0, 0, 0), 20).print(screen, (SIZE[0]//2-200, SIZE[1]//2-100), False)
                Text(self.texts[3], (0, 0, 0), 20).print(screen, (SIZE[0]//2-200, SIZE[1]//2-50), False)
                for i in range(len(self.points)):
                    if self.points[i] == 0:
                        pygame.draw.circle(screen, (128, 128, 128), (SIZE[0]//2-220, SIZE[1]//2-200+i*50+5), 10)
                    elif self.points[i] == 1:
                        pygame.draw.circle(screen, (0, 0, 255), (SIZE[0]//2-220, SIZE[1]//2-200+i*50+5), 10)
                    elif self.points[i] == 2:
                        pygame.draw.circle(screen, (255, 0, 0), (SIZE[0]//2-220, SIZE[1]//2-200+i*50+5), 10)
                    elif self.points[i] == 3:
                        pygame.draw.circle(screen, (0, 255, 0), (SIZE[0]//2-220, SIZE[1]//2-200+i*50+5), 10)
            else:
                Text(self.player.name, (0, 0, 0), 20).print(screen, (SIZE[0]//2-200, SIZE[1]//2-200), False)
                print(self.other_players)
                for i, player in enumerate(self.other_players):
                    Text(player["name"], (0, 0, 0), 20).print(screen, (SIZE[0]//2-200, SIZE[1]//2-150+i*50), False)
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
            if self.winner == PlayerRole.CATCHER:
                Text("CATCHER WIN", COLORS['catcher'], 50).print(screen, (SIZE[0]//2, SIZE[1]//2), True)
            else:
                Text("RUNNER WIN", COLORS['runner'], 50).print(screen, (SIZE[0]//2, SIZE[1]//2), True)


        