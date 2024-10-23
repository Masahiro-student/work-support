#手探り間隔の拡張

import numpy as np
import traceback
import cv2
import time
import datetime
from PIL import Image
from kinect import Kinect
import hand_detection as hd
import m2 as md
import object_detection as od
from hand_detection.hand import Hand
from marker2 import Marker
from object import Object
from motor_controller import MotorController 

num_time = 3

min_th_h = None
max_th_h = None
min_th_m = None
max_th_m = None
min_th_o = None
max_th_o = None
mask = None
manager = None
radius = 40
motor_power = 200

prob = 0.15

last_time = time.time()
data = []
mc = MotorController()

object_pt1 = (350, 200)
object_pt2 = (400, 300)
object_polygon = np.array([[350, 200], [350, 300], [400, 200], [400, 300]])
line_pt1 = ()
line_pt2 = ()

class Goal:
    pos = None
    radius = None

    def __init__(self, u, v, radius):
        self.pos = np.array([u, v])
        self.radius = radius

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

tools = [
    Goal(700, 220, radius)  
]

class State:
    assem = None
    target = None
    
    def __init__(self, assem, target):
        self.assem = assem
        self.target = target


def load_mask():
    mask = Image.open("/home/toyoshima/script/hand_detection/mask.png")
    # mask = Image.open("mask.png")
    return np.asarray(mask)

def load_mask2():
    mask = np.zeros((720,1280))
    for i in range(285, 915):
        for j in range(173, 612):
            mask[j][i] = 1
    return mask

def load_threshold_h():
    return hd.load_hs_threshold("hand_threshold3")

def load_threshold_m():
    return md.load_hs_threshold("marker_threshold2")

def load_threshold_o():
    return od.load_hs_threshold("cardboard_threshold")

def kinect_color():
    kinect = Kinect()
    def get_color():
        kinect.update()
        return kinect.color_arr

    return get_color

get_color_arr = kinect_color()           

def get_hand(color_arr):
    contour = hd.detect_hand(
        color_arr,
        min_th_h,
        max_th_h,
        mask,
    )
    return Hand(contour)

def search_object(in_out):
    if in_out == 1:
        mc.drive_all(255)
    elif in_out == 0:
        mc.drive_all(255)
    else:
        mc.stop()


def guide2(hand, target):
    dx = target.pos[0] - hand.center[0]
    dy = target.pos[1] - hand.center[1]
    dist = np.sqrt(dx*dx + dy*dy)
    if dist > 200:
        for i in range(4):
            mc.send_pwm(i, 0)
    elif 200 >= dist > 150:
        for i in range(4):
            mc.send_pwm(i, 50)
    elif 150 >= dist > 100:
        for i in range(4):
            mc.send_pwm(i, 100)
    elif 100 >= dist > 50:
        for i in range(4):
            mc.send_pwm(i, 150)
    elif 50 >= dist > 0:
        for i in range(4):
            mc.send_pwm(i, 200)

def wall(hand):
    if 420 > hand.center[1] > 400:
        for i in range(4):
            mc.send_pwm(i, 200)
    else:  
        for i in range(4):
            mc.send_pwm(i, 0)

def direction_vib(c0, c1):
    x1 = int(c0[0]) 
    y1 = int(c0[1])
    x2 = int(c1[0])
    y2 = int(c1[1])
    if x2 == x1:
        x_1 = x1
        y_1 = 0
        x_2 = x2
        y_2 = 720
    else:  
        a = (y2 - y1)/(x2 - x1)
        b = y1 - a * x1

        x_1 = 0
        y_1 = int(a * x_1 + b)

        x_2 = 1028
        y_2 = int(a * x_2 + b)    


def vibe():
    for i in range(4):
        mc.send_pwm(i, 10)
       

def reached(hand, target):
    return target.include(hand.center)

def toward_tool(start_time, count, r):
    points = []

    target = tools[r]
    flag = True

    hand = Hand(min_th_h, max_th_h, mask)
    marker = Marker(min_th_m, max_th_m, mask)
    object = Object(min_th_o, max_th_o, mask)
    '''color_arr = get_color_arr()
    marker2 = np.array(md.detect_marker(color_arr, min_th_m, max_th_m, mask))
    print(marker2[1])'''
    '''color_arr = get_color_arr()
    marker2 = md.detect_marker(color_arr, min_th_m, max_th_m, mask)
    print(marker2[1])'''
    t2 = time.time()
    pre_t = time.time()
    while flag:
        color_arr = get_color_arr()  #kinectから色情報（配列）を取得

        hand.update(color_arr)
        marker.update(color_arr)
        object.update(color_arr)

        center = marker.compute_center()

        tt = time.time()
        dt = tt - pre_t
        
        if dt < 0.084:
            time.sleep(0.084 - dt)

        draw_marker(color_arr, marker)
        end_t = time.time()
        pre_t = end_t


        draw_marker_direction2(color_arr,center, hand.center)
        draw_imaginary_object(color_arr)

        search_object(line_in_object2(object_polygon, center, hand.center))

        flag = draw(color_arr, hand,  target)

       

def finish():
    now = datetime.datetime.now()
    np.savetxt('exp_data/data' + now.strftime('%Y%m%d_%H%M%S') + '.csv', data)
    exit(0)

def draw(color_arr, hand, target):  
    cv2.drawContours(      #緑で手の輪郭を描画
        color_arr,
        hand.contour,
        -1,
        color=(0, 255, 0))

    cv2.circle(            #緑で手の重心を描画
        color_arr,
        (int(hand.center[0]), int(hand.center[1])),
        10,
        color=(0, 255, 0),
        thickness=-1
        )
        
    
    draw_goals(color_arr, target)
    draw_table(color_arr)
    cv2.imshow("img", color_arr)
    
    key = cv2.waitKey(1)
    if key == ord("q"):
        return False
    else:
        return True

    
def draw_goals(img, target):
    for t in tools:
        t.draw(
            img,
            color=(255, 0, 0)
        )
    color = (0, 0, 255)

def draw_table(img):
    cv2.rectangle(
        img,
        (279, 170),
        (922, 616),
        color=(0, 255, 0),
        thickness=2
    )

def draw_marker(img, marker):
    cv2.drawContours(      #青でマーカーの輪郭を描画
        img,
        marker.contour,
        -1,
        color=(255, 0, 0))

    cv2.circle(            #青でマーカーの重心を描画
        img,
        (int(marker.center[0]), int(marker.center[1])),
        5,
        color=(0, 0, 0),
        thickness=-1
        )
    
def draw_marker2(img, marker, c0, c1):
    cv2.drawContours(      #青でマーカーの輪郭を描画
        img,
        marker.contour,
        -1,
        color=(255, 0, 0))

    cv2.circle(            #青でマーカーの重心を描画
        img,
        (int(c0[0]), int(c0[1])),
        5,
        color=(0, 0, 0),
        thickness=-1
        )
    
    cv2.circle(            #青でマーカーの重心を描画
        img,
        (int(c1[0]), int(c1[1])),
        5,
        color=(0, 0, 0),
        thickness=-1
        )
    
def draw_imaginary_object(img):
    cv2.rectangle(
        img,
        object_pt1,
        object_pt2,
        color=(0, 255, 0),
        thickness=2
    )

def draw_imaginary_line(img):
    cv2.line(
        img,
        line_pt1,
        line_pt2,
        color=(0, 255, 0),
        thickness=2
    )
    
def draw_object(img, object):
    cv2.drawContours(      #緑で手の輪郭を描画
        img,
        object.contour,
        -1,
        color=(0, 0, 255))

    cv2.circle(            #青でマーカーの重心を描画
        img,
        (int(object.center[0]), int(object.center[1])),
        5,
        color=(255, 255, 255),
        thickness=-1
        )

def draw_marker_direction(img, c0, c1):
    cv2.line(img, 
            (int(c0[0]), int(c0[1])), 
            (int(c1[0]), int(c1[1])), 
                    color=(0, 0, 255), 
                    thickness=1
    )

def draw_marker_direction2(img, c0, c1):
    x1 = int(c0[0]) 
    y1 = int(c0[1])
    x2 = int(c1[0])
    y2 = int(c1[1])
    if x2 == x1:
        x_1 = x1
        y_1 = 0
        x_2 = x2
        y_2 = 720
    else:  
        a = (y2 - y1)/(x2 - x1)
        b = y1 - a * x1

        x_1 = 0
        y_1 = int(a * x_1 + b)

        x_2 = 1028
        y_2 = int(a * x_2 + b)

    cv2.line(img, 
            (x_1, y_1), 
            (x_2, y_2), 
                    color=(255, 0, 0), 
                    thickness=1
    )

def draw_direction(img,a,b, center):
    # cv2.line(img,
    #         # (0,b),
    #         # (1280,1280*a + b),
    #         (0,32),
    #         (1280,12),
    #         color=(0, 255, 0),
    #         thickness=3,
    #         lineType=cv2.LINE_4,
    #         shift=0  
    #         )
    center = center.astype(int)
    #(center)
    h, w = center
    w_hat = w + 100
    h_hat = int(a*w_hat + b)
    cv2.line(img, 
            (h, w), 
            (h_hat, w_hat), 
            color=(0, 0, 255), 
             thickness=1
    )
    ''' w, h= center
    w_hat = w + 100
    h_hat = int(a*w_hat + b)
    cv2.arrowedLine(img, 
                    (w, h), 
                    (w_hat,h_hat), 
                    color=(0, 0, 255), 
                    thickness=1
    )'''

def line_in_object(contour, c0, c1):
    #np_object = np.array(contour)
    #np_object2 = np.squeeze(np_object)
    x1 = int(c0[0]) 
    y1 = int(c0[1])
    x2 = int(c1[0])
    y2 = int(c1[1])
    if x2 == x1:
        threshold = 5
        for point in contour:
            x = int(point[0])
            if abs(x - x1) < threshold:
                return True
        return False

        
    else:  
        a = (y2 - y1)/(x2 - x1)
        b = y1 - a * x1
        threshold = 5
        question = False
        for point in contour:
            x = int(point[0])
            y = int(point[1])
            y_pred = a * x + b
            if abs(y - y_pred) < threshold:
                question = True
                return question
        return question


def line_in_object2(polygon, c0, c1):
    #np_object = np.array(contour)
    #np_object2 = np.squeeze(np_object)
    x1 = int(c0[0]) 
    y1 = int(c0[1])
    x2 = int(c1[0])
    y2 = int(c1[1])
    if x2 == x1:
        if polygon[0][0] < x1 and x1 < polygon[3][0]:
            return 1
        elif polygon[0][0] == x1 or x1 == polygon[3][0]:
            return 0
        else:
            return -1
          
    else:  
        a = (y2 - y1)/(x2 - x1)
        b = y1 - a * x1
        question = -1
        for x in range(279, 923):
            y = a * x + b
            if  cv2.pointPolygonTest(polygon, (x,y), False) == 1:
                question = 1
                return question
            elif cv2.pointPolygonTest(polygon, (x,y), False) == 0:
                question = 0
        return question



def init():
    global mask, min_th_h, max_th_h, min_th_m, max_th_m, min_th_o, max_th_o,manager
    mask = load_mask2()
    (min_th_h, max_th_h) = load_threshold_h()
    (min_th_m, max_th_m) = load_threshold_m()
    (min_th_o, max_th_o) = load_threshold_o()
    # atexit.register(mc.stop_motor)

def main():
    init()
    toward_tool(time.time(), 1, 0)

if __name__ =="__main__":
    try:
        main()
    except KeyboardInterrupt:
        mc.stop()
    except Exception as e:
        print(traceback.format_exc())
        print(e)
    
