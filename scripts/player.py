from enum import Enum
import pymunk, pygame
from math import cos, sin, atan2

from scripts.UI.text import Text
import scripts.settings as s
from scripts.settings import COLORS, PLAYER_MASS, PLAYER_RADIUS, PLAYER_ELASTICITY, PLAYER_FRICTION, PLAYER_SPEED, DUMPING


class PlayerRole(Enum):
    CATCHER = 1
    RUNNER = 2


class Player:

    def __init__(self, uuid: str, name: str, role: PlayerRole, pos: list[float, float]) -> None:
        self.uuid = uuid
        self.name = name
        self.role = role

        self.moment = pymunk.moment_for_circle(PLAYER_MASS, 0, PLAYER_RADIUS)
        self.body = pymunk.Body(PLAYER_MASS, self.moment, pymunk.Body.DYNAMIC)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, PLAYER_RADIUS)
        self.shape.elasticity = PLAYER_ELASTICITY

        self.is_moving = False
        self.movement_is_blocked = False

        self.force = [0, 0]
    
    def set_pos(self, x, y):
        self.body.position = (x, y)

    def get_pos(self):
        return self.body.position.x, self.body.position.y
    
    def add_to_space(self, space: pymunk.Space) -> None:
        space.add(self.body, self.shape)

    def start_move(self) -> None:
        self.is_moving = True

    def stop_move(self) -> None:
        self.is_moving = False

    def block_movement(self) -> None:
        self.movement_is_blocked = True

    def unblock_movement(self) -> None:
        self.movement_is_blocked = False

    def update(self, mouse_pos: float) -> None:
        if self.is_moving and not self.movement_is_blocked:
                # Convert body pos and target pos to angle
                vector = (mouse_pos[0] - self.body.position.x, mouse_pos[1] - self.body.position.y)
                angle = atan2(vector[1], vector[0])
                # Calculate force
                self.force = [cos(angle) * PLAYER_SPEED, sin(angle) * PLAYER_SPEED]
                self.body.apply_force_at_local_point(self.force, (0, 0))
        else:
            self.body.velocity = (self.body.velocity[0] * DUMPING, self.body.velocity[1] * DUMPING)
        
        self.force = [0, 0]
            

    def draw(self, screen, camera) -> None:
        self.body.angular_velocity = 0
        x, y = camera.get_local_point(self.body.position.x, self.body.position.y)
        r = camera.get_local_radius(PLAYER_RADIUS)
        if self.role == PlayerRole.CATCHER:
            pygame.draw.circle(screen, COLORS['catcher'], (x, y), r)
        else:
            pygame.draw.circle(screen, COLORS['runner'], (x, y), r)

        if s.DEBUG:
            Text(f"Pos: {int(self.body.position.x)}, {int(self.body.position.y)}", (0, 0, 0), 14).print(screen, (x+20, y-40))
            Text(f"Velocity: {int(self.body.velocity.x)}, {int(self.body.velocity.y)} ({int(abs(self.body.velocity.x)+abs(self.body.velocity.y))})", (0, 0, 0), 14).print(screen, (x+20, y-30))

            Text(f"Radius: {PLAYER_RADIUS}", (0, 0, 0), 14).print(screen, (x+20, y-20))