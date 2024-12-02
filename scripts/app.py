import pygame

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

        # Set model variables
        self.camera = Camera(x=0, y=0, distance=10, resolution=self.size)
        # This line takes data from save file
        self.field = Field()

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
                if event.button == 1:
                    pass
                elif event.button == 3:
                    pass

            if event.type == pygame.KEYDOWN:  # If key button down...
                if event.key == pygame.K_SPACE:
                    pass

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
        self.field.update(self.dt)
        # -*-*-               -*-*-

        # -*-*- Rendering Block -*-*-
        self.screen.fill(self.colors['background'])  # Fill background

        self.field.draw(self.screen, self.camera)

        self.camera.draw_map_scale(self.screen, offset=(140, 15))  # Draw map scale
        Text("FPS: " + str(int(self.clock.get_fps())), [0, 0, 0], 20).print(self.screen,
                                                                            [self.width - 70, self.height - 21],
                                                                            False)  # FPS counter
        # -*-*-                 -*-*-

        # -*-*- Update Block -*-*-
        pygame.display.update()

        self.dt = self.clock.tick(self.fps)
        # -*-*-              -*-*-


def close():
    pygame.quit()
    exit()
