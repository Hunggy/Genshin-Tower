import random
from .config import SCREEN_W, SCREEN_H


class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, SCREEN_W)
        self.y = random.randint(0, SCREEN_H)
        self.size = random.randint(1, 3)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(50, 150)
        self.color = (200 + random.randint(0, 55), 200 + random.randint(0, 55), 255)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x < 0 or self.x > SCREEN_W or self.y < 0 or self.y > SCREEN_H:
            self.reset()
