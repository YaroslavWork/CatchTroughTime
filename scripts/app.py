import pygame
import pymunk.pygame_util
import pymunk
import random

from scripts.player import Player, PlayerRole
import scripts.settings as s
from scripts.camera import Camera
from scripts.field import Field
from scripts.UI.text import Text


class App:

    def __init__(self) -> None:
        # Initialize pygame and settings
        pygame.init()

        self.size = self.width, self.height = s.SIZE
        self.name = s.NAME
        self.colors = s.COLORS
        self.fps = s.FPS

        # Set pygame window
        pygame.display.set_caption(self.name)

        # Set pygame clock
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

        # Set input variables
        self.dt = 0
        self.mouse_pos = (0, 0)
        self.keys = []

        # Pymunk configuration
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)

        # Set model variables
        self.camera = Camera(x=0, y=0, distance=1000, resolution=self.size)
        self.player = Player(uuid="1", name="", role=PlayerRole.RUNNER, pos=(100, 10))
        with open('conf/player_name.txt', 'r') as file:
            self.player.name = file.read().strip() + str(random.randint(0, 10000))  # TESTS IN MY LOCAL MACHINE
        # TODO: DELETE RANDOM PART LATER
        self.player.add_to_space(self.space)
        self.field = Field(self.space, self.player)

        
        

        
    def update(self) -> None:
        """
        Main update function of the program.
        This function is called every frame
        """

        # -*-*- Input Block -*-*-
        self.mouse_pos = pygame.mouse.get_pos()  # Get mouse position

        for event in pygame.event.get():  # Get all events
            if event.type == pygame.QUIT:  # If you want to close the program...
                close()
                Text.fonts = {}  # Clear fonts

            if event.type == pygame.MOUSEBUTTONDOWN:  # If mouse button down...
                if event.button == 1:  # Left mouse button
                    self.player.start_move()
                elif event.button == 3:  # Right mouse button
                    pass

            if event.type == pygame.MOUSEBUTTONUP:  # If mouse button up...
                if event.button == 1:  # Left mouse button
                    self.player.stop_move()

            if event.type == pygame.KEYDOWN:  # If key button down...
                if event.key == pygame.K_SPACE:
                    self.field.connect_to_server()
                if event.key == pygame.K_BACKSPACE:
                    s.DEBUG = not s.DEBUG
                if event.key == pygame.K_r:
                    self.field.start_countdown()
                if event.key == pygame.K_l:
                    self.field.launch_simulation()

        self.keys = pygame.key.get_pressed()  # Get all keys (pressed or not)
        if self.keys[pygame.K_LEFT] or self.keys[pygame.K_a]:
            self.camera.move_left(1, self.dt)
        if self.keys[pygame.K_RIGHT] or self.keys[pygame.K_d]:
            self.camera.move_right(1, self.dt)
        if self.keys[pygame.K_UP] or self.keys[pygame.K_w]:
            self.camera.move_up(1, self.dt)
        if self.keys[pygame.K_DOWN] or self.keys[pygame.K_s]:
            self.camera.move_down(1, self.dt)
        if self.keys[pygame.K_e]:
            self.camera.scale_in(1, self.dt)
        if self.keys[pygame.K_q]:
            self.camera.scale_out(1, self.dt)
        # -*-*-             -*-*-

        # -*-*- Physics Block -*-*-
        self.space.step(self.dt / 1000)
        self.field.update(self.dt, self.camera.get_global_point(*self.mouse_pos))
        
        # -*-*-               -*-*-

        # -*-*- Rendering Block -*-*-
        self.screen.fill(self.colors['background'])  # Fill background

        self.field.draw(self.screen, self.camera)

        if s.DEBUG: 
            screen_pos = self.mouse_pos
            global_pos = self.camera.get_global_point(*screen_pos)
            if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking text
                Text("DEBUG MODE", (255, 0, 0), 20).print(self.screen, (10, 10))
            Text(f"Screen pos: {screen_pos[0]}, {screen_pos[1]}", (0, 0, 0), 14).print(self.screen, (self.mouse_pos[0]+20, self.mouse_pos[1]-20))
            Text(f"Global pos: {int(global_pos[0])}, {int(global_pos[1])}", (0, 0, 0), 14).print(self.screen, (self.mouse_pos[0]+20, self.mouse_pos[1]-10))

            self.camera.draw_map_scale(self.screen, offset=(140, 15))  # Draw map scale
            Text("FPS: " + str(int(self.clock.get_fps())), [0, 0, 0], 20).print(self.screen, [self.width - 70, self.height - 21], False)  # FPS counter
        # -*-*-                 -*-*-

        # -*-*- Update Block -*-*-
        pygame.display.update()

        self.dt = self.clock.tick(self.fps)
        # -*-*-              -*-*-


def close():
    pygame.quit()
    exit()