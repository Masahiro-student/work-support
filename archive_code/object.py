import numpy as np
import object_detection as od

def compute_center(contour):   #輪郭の座標の集合の平均から重心を求める
    if len(contour) == 0:
        return np.array([0, 0])
    concatenated_contour = np.concatenate(np.concatenate(contour))
    return np.mean((concatenated_contour), axis=0)

class Object:
    def __init__(self, min_th, max_th, mask):
        self.min_th = min_th
        self.max_th = max_th
        self.mask = mask

    def compute_center(self):
        if len(self.contour) == 0:
            return np.array([0, 0])
        concatenated_contour = np.concatenate(np.concatenate(self.contour))
        return np.mean((concatenated_contour), axis=0)
    
    def distance(self, goal):   #おそらく使われていない
        dx = self.center[0] - goal.u
        dy = self.center[1] - goal.v
        distance = dx*dx + dy*dy
        return np.sqrt(distance)

    def update(self, color_arr):
        contour = od.detect_object(
            color_arr,
            self.min_th,
            self.max_th,
            self.mask,
        )
        self.contour = contour

        self.center = self.compute_center()

    def direction(self):
        np_hand = np.array(self.contour)
        c = np.squeeze(np_hand)
        x = c[:,1]
        y = c[:,0]

        def reg1dim(x, y):
            n = len(x)
            a = ((np.dot(x, y)- y.sum() * x.sum()/n)/
               ((x ** 2).sum() - x.sum()**2 / n))
            b = (y.sum() - a * x.sum())/n
            return a, b

        a, b = reg1dim(x, y)
        return a, b
