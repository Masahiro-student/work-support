'''
手の方向出る x方向について止まると今の位置に吸収 人工筋肉あり
ゴム部品ある位置に3回手が到達,黄色チューブの位置に一回到達完了で取ってくるタスク完了
棚まで行く前は手探り振動,戻りは格子振動,手前まで来たら手探り振動
'''
import numpy as np
import atexit
import traceback
import os
import cv2
import time
import datetime
import csv
import random
from PIL import Image
from kinect import Kinect
import hand_detection as hd
import m3 as md
from hand_detection.hand import Hand
from hand_detection.marker import Marker
from module_controller import ModuleController 
import matplotlib.pyplot as plt
import hand_detection.trajectory as tr
import hand_detection.kalmanfilter as klf
from glob import glob

min_th_h = None
max_th_h = None
min_th_m = None
max_th_m = None
min_th_o = None
max_th_o = None
mask = None
mask2 = None
manager = None
trajectory = None

radius = 35


begin_time = None

frame_width = int(1280)
frame_height = int(720)
fps = float(13)

last_time = time.time()
data = []
mc = ModuleController()

line1_pt1 = (401, 170)
line1_pt2 = (421, 620)
line1_polygon = np.array([[401, 170], [401, 620], [421, 170], [421, 620]])
line2_pt1 = (527, 170)
line2_pt2 = (547, 620)
line2_polygon = np.array([[527, 170], [527, 620], [547, 170], [547, 620]])
line3_pt1 = (653, 170)
line3_pt2 = (673, 620)
line3_polygon = np.array([[653, 170], [653, 620], [673, 170], [673, 620]])
line4_pt1 = (779, 170)
line4_pt2 = (799, 620)
line4_polygon = np.array([[779, 170], [779, 620], [799, 170], [799, 620]])
bar1_pt1 = (279, 273)
bar1_pt2 = (922, 293)
bar1_polygon = np.array([[279, 273], [922, 293], [799, 273], [922, 293]])
bar2_pt1 = (279, 383)
bar2_pt2 = (922, 403)
bar2_polygon = np.array([[279, 383], [922, 403], [799, 383], [922, 403]])
bar3_pt1 = (279, 493)
bar3_pt2 = (922, 513)
bar3_polygon = np.array([[279, 493], [922, 513], [799, 493], [922, 513]])

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
    Goal(695, 215, radius), 
    Goal(880, 215, radius)
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

def load_mask_hand():
    mask = np.zeros((720,1280))
    for i in range(285, 915):
        for j in range(173, 612):
            mask[j][i] = 1
    return mask

def load_mask_marker():
    mask = np.zeros((720,1280))
    for i in range(285, 915):
        for j in range(255, 612):
            mask[j][i] = 1
    return mask

def load_threshold_h():
    return hd.load_hs_threshold("hand_threshold")

def load_threshold_m():
    return md.load_hs_threshold("marker_threshold")

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
        mc.send_pwm(0,100)
    elif in_out == 0:
        mc.send_pwm(0,100)
    else:
        mc.send_pwm(0,0)

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
       
def reached(hand, target):
    return target.include(hand.center)

def toward_tool(start_time, count):
    now = datetime.datetime.now()

    tar_name = 'sawada'
    base_dir = f'/home/toyoshima/script/hand_detection/exp_no_support/{tar_name}'
    directory_path = os.path.join(base_dir, "traj_time")
    directory_path_v = os.path.join(base_dir, "kinect_movie")

    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(directory_path, exist_ok=True)
    os.makedirs(directory_path_v, exist_ok=True)

    dir_length = len(glob(os.path.join(directory_path_v, '*')))

    file_name = f"traj_time_{now.strftime('%Y%m%d_%H%M%S')}_{dir_length}.npy"
    full_path = os.path.join(directory_path, file_name)

    file_name_v = f"kinect_movie_{now.strftime('%Y%m%d_%H%M%S')}_{dir_length}.mp4"
    full_path_v = os.path.join(directory_path_v, file_name_v)

    #output_file = "output_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(full_path_v, fourcc, fps, (frame_width, frame_height), True)

    flag = True

    hand = Hand(min_th_h, max_th_h, mask)
    marker = Marker(min_th_m, max_th_m, mask2)
 
    '''color_arr = get_color_arr()
    marker2 = np.array(md.detect_marker(color_arr, min_th_m, max_th_m, mask))
    print(marker2[1])'''
    '''color_arr = get_color_arr()
    marker2 = md.detect_marker(color_arr, min_th_m, max_th_m, mask)
    print(marker2[1])'''
    trajectory = tr.Trajectory(1280, 720)
    begin_time = time.time()

    while flag:
        color_arr = get_color_arr()  #kinectから色情報（配列）を取得
        frame = color_arr[:, :, :3]
        out.write(frame)

        hand.update(color_arr)
        marker.update(color_arr)
        center = marker.compute_center()
        trajectory.push_point(hand.center, time.time() - begin_time) 
        
        draw_marker(color_arr, marker)
        draw_marker_direction2(color_arr,center, hand.center)  #予測していない手の方
        draw_hand(color_arr, hand)
  

        flag = draw(color_arr)

    out.release()


    traj = np.array(trajectory.trajectory)
    #print(traj)

    np.save(full_path, traj)


def finish():
    now = datetime.datetime.now()
    np.savetxt('exp_data/data' + now.strftime('%Y%m%d_%H%M%S') + '.csv', data)
    exit(0)

def draw_hand(color_arr, hand):  
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
    return time.time()

def draw1(color_arr):
    #draw_goals(color_arr)
    draw_table(color_arr)
    cv2.imshow("img", color_arr)
    
    key = cv2.waitKey(1)
    if key == ord("q"):
        return False
    else:
        return True
        
def draw(color_arr):
    #draw_goals(color_arr)
    draw_table(color_arr)
    cv2.imshow("img", color_arr)
    
    key = cv2.waitKey(1)
    if key == ord("q"):
        return False
    else:          
        return True

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
    
def draw_prediction(img,point):
    cv2.circle(            #青でマーカーの重心を描画
            img,
            (int(point[0]), int(point[3])),
            5,
            color=(0, 0, 255),
            thickness=-1
            )
    
def draw_point(img, x, y):
    cv2.circle(            #青でマーカーの重心を描画
            img,
            (int(x), int(y)),
            5,
            color=(0, 0, 255),
            thickness=-1
            )

def draw_imaginary_line(img, line_pt1, line_pt2):
    cv2.rectangle(
        img,
        line_pt1,
        line_pt2,
        color=(255, 0, 0),
        thickness=2
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

def draw_marker_direction3(img, c0, c1):
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
                    color=(0, 0, 255), 
                    thickness=1
    )

def init():
    global mask, mask2, min_th_h, max_th_h, min_th_m, max_th_m, min_th_o, max_th_o,manager, begin_time
    mask = load_mask_hand()
    mask2 = load_mask_marker()
    (min_th_h, max_th_h) = load_threshold_h()
    (min_th_m, max_th_m) = load_threshold_m()
    '''(min_th_o, max_th_o) = load_threshold_o()'''
    # atexit.register(mc.stop_motor)

def main():
    init()
    toward_tool(time.time(), 1)

if __name__ =="__main__":
    try:
        main()
    except KeyboardInterrupt:
        mc.allmotor_stop()
        mc.comp_stop()
    except Exception as e:
        print(traceback.format_exc())
        print(e)