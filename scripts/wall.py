import pygame
import pymunk


class Wall:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect

        self.body = None
        self.shape = None

    def create_rectangle(self, space):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = self.rect.left, self.rect.top
        vertices = [
            (-self.rect.width / 2, -self.rect.height / 2),
            (-self.rect.width / 2, self.rect.height / 2),
            (self.rect.width / 2, self.rect.height / 2),
            (self.rect.width / 2, -self.rect.height / 2)
        ]
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.friction = 1

        space.add(self.body, self.shape)

    def draw(self, screen, camera):
        local_vertices = [camera.get_local_point(self.body.position.x+v[0], self.body.position.y+v[1]) for v in self.shape.get_vertices()]
        pygame.draw.polygon(screen, (0, 0, 0), local_vertices)

        