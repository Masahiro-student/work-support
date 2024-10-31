import numpy as np
from object import Object

class Table (Object):
    def __init__(self, top_left, bottom_right):
        super().__init__(top_left, bottom_right)
        
    def load_mask(self):
        mask = np.zeros((720,1280))
        mask = np.zeros((720, 1280))  # 全体が0の配列を生成
        x1, y1 = self.top_left
        x2, y2 = self.bottom_right
        mask[y1:y2, x1:x2] = 1  # 指定範囲のみ1に設定
        return mask
        
        