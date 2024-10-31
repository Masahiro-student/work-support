import os
import numpy as np
import cv2

class Object:
    def __init__(self, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right
    
    #テーブル(作業場所)や棚の座標など固定する物体の座標をロードする関数
    def load_coordinates(file_name):
        file_path = os.path.join(os.path.dirname(__file__), "coordinates_file", f"{file_name}.txt")
        coordinates_arr = np.loadtxt(file_path)
        return coordinates_arr
    
    def draw_rectangle(self, canvas, color):
        return cv2.rectangle(
        canvas,
        self.top_left,
        self.bottom_right,
        color,
        thickness=2
        )
        
    
