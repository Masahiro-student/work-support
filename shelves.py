import numpy as np
import cv2

class Shelves:    #4つの棚に配置する丸(正しい部品があるときに丸を表示)
    def __init__(self, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right
        
        self.x_center = (top_left[0] + bottom_right[0]) / 2
        self.y_center = (top_left[1] + bottom_right[1]) / 2
        self.center = (self.x_center, self.y_center)
        
        self.radius = 75


    def include(self, p):
        dx = self.center[0] - p[0]
        dy = self.center[1] - p[1]

        return dx*dx + dy*dy < self.radius * self.radius

    def draw_circle(self, canvas, color): 
        return cv2.circle(
            canvas,
            (self.pos[0], self.pos[1]),
            self.radius,
            color,
            thickness=2
        )
        
    def draw_rectangle(self, canvas, color):
        return cv2.rectangle(
        canvas,
        self.top_left,
        self.bottom_right,
        color,
        thickness=2
        )
        
    
    