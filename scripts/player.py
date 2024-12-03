from enum import Enum
import pymunk, pygame
from math import cos, sin, atan2

from scripts.settings import PLAYER_MASS, PLAYER_RADIUS, PLAYER_ELASTICITY, PLAYER_FRICTION, PLAYER_SPEED, DUMPING


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
        self.shape.friction = PLAYER_FRICTION

        self.is_moving = False

        self.force = [0, 0]
    
    def add_to_space(self, space: pymunk.Space) -> None:
        space.add(self.body, self.shape)

    def start_move(self) -> None:
        self.is_moving = True

    def stop_move(self) -> None:
        self.is_moving = False

    def update(self, mouse_pos: float) -> None:
        if self.is_moving:
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
        pygame.draw.circle(screen, (0, 128, 255), (x, y), r)