import numpy as np
import cv2

class Shelves:    #4つの棚に配置する丸(正しい部品があるときに丸を表示)
    pos = None
    radius = None

    def __init__(self, u, v, radius, height, width):
        self.pos = np.array([u, v])
        self.radius = radius

        self.h_max = v + height // 2
        self.h_min = v - height // 2

        self.w_max = u + width // 2
        self.w_min = u - width // 2

    def include(self, p):
        dx = self.pos[0] - p[0]
        dy = self.pos[1] - p[1]

        return dx*dx + dy*dy < self.radius * self.radius

    def draw(self, canvas, color): 
        return cv2.circle(
            canvas,
            (self.pos[0], self.pos[1]),
            self.radius,
            color=color,
            thickness=2
        )