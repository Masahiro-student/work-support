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
#import object_detection as od
from hand_detection.hand import Hand
from hand_detection.marker import Marker
from object import Object
#import motor_controller3 as mc
from module_controller import ModuleController 
import matplotlib.pyplot as plt
import hand_detection.trajectory as tr
import hand_detection.kalmanfilter as klf
#import kalmanfilteronesetstop as klf
import math

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
fps = float(11)

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
    return hd.load_hs_threshold("hand_threshold3")

def load_threshold_m():
    return md.load_hs_threshold("marker_threshold4")

'''def load_threshold_o():
    return od.load_hs_threshold("cardboard_threshold")'''

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
       

def toward_tool(start_time, count):
    now = datetime.datetime.now()
    directory_path_v = "/home/toyoshima/script/hand_detection/exp_module/kinect_movie"
    file_name_v = f"kinect_movie_{now.strftime('%Y%m%d_%H%M%S')}.mp4"
    full_path = os.path.join(directory_path_v, file_name_v)
    #output_file = "output_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(full_path, fourcc, fps, (frame_width, frame_height), True)
    
    T=[]
    dt = 0.1
    t = 0
    
    blackrubber = tools[0]
    yellowtube = tools[1]

    flag = True
    blackrubber_count = 0
    yellowtube_count = 0
    hand = Hand(min_th_h, max_th_h, mask)
    marker = Marker(min_th_m, max_th_m, mask2)
    print(min_th_m, max_th_m)
    '''color_arr = get_color_arr()
    marker2 = np.array(md.detect_marker(color_arr, min_th_m, max_th_m, mask))
    print(marker2[1])'''
    '''color_arr = get_color_arr()
    marker2 = md.detect_marker(color_arr, min_th_m, max_th_m, mask)
    print(marker2[1])'''
    trajectory = tr.Trajectory(1280, 720)
    previous_time = time.time()

    x = np.array([0, 0, 0, 0, 0, 0])
    xm1 = np.array([0, 0, 0, 0, 0, 0])
    P = np.eye(6)
    Pm1 = np.eye(6)
    previous_previous_x = [0,0]
    previous_x = [0,0]
    time.sleep(1)
    mc.comp_start()
    #mc.mod(1)
    mc.valve(0,1)
    mc.valve(1,1)
    mc.valve(2,1)
    mc.pressure(200)
    begin_time = time.time()
    pre_t = 0
    six_two_count = 0
    wrong_place_count = 0
    not_wrong_place_count = 0
    while flag:
        color_arr = get_color_arr()  #kinectから色情報（配列）を取得
        t1 = time.time()
        frame = color_arr[:, :, :3]
        out.write(frame)

        hand.update(color_arr)
        marker.update(color_arr)
        center = marker.compute_center()
        trajectory.push_point([x[0],x[3]], time.time() - begin_time) 
        ddt = t1 - pre_t
        #print(ddt)
        pre_t = t1
        if previous_previous_x is not None:
            previous_previous_x = previous_x
        previous_x = x
        x, P, h_pred3 = klf.kalman_filter(x, P, np.array(hand.center))
        xm1, Pm1, h_pred3_1 = klf.kalman_filter(xm1, Pm1, np.array(center))

        deltax = math.sqrt((previous_x[0] - x[0])**2 + (previous_x[3] - x[3])**2)
        deltadeltax = abs(previous_previous_x - x[0])

        
        draw_marker2(color_arr, xm1, marker)
        draw_marker_direction2(color_arr,[xm1[0],xm1[3]], [x[0],x[3]])  #予測していない手の方向
        
        draw_imaginary_object(color_arr)
        draw_imaginary_line(color_arr, bar1_pt1, bar1_pt2)
        draw_imaginary_line(color_arr, bar2_pt1, bar2_pt2)
        draw_imaginary_line(color_arr, bar3_pt1, bar3_pt2)
        #print(six_two_count)
        print(wrong_place_count)
        #if deltax < 10 and deltadeltax <10:
        if blackrubber_count == 6 and yellowtube_count == 2:
            six_two_count = six_two_count + 1
        if six_two_count == 1:
            mc.valve(0,0)
            mc.valve(1,0)
            mc.valve(2,0)
        if six_two_count == 10:
            mc.valve(0,1)
            mc.valve(1,1) 
            mc.valve(2,1)       

        if in_wrong_place([x[0],x[3]]):
            wrong_place_count = wrong_place_count + 1
            not_wrong_place_count = 0
            if wrong_place_count % 4 == 1:
                mc.send_pwm(12,100)
                mc.send_pwm(13,100)
            elif wrong_place_count % 4 == 3:
                mc.send_pwm(12,0)
                mc.send_pwm(13,0)                
        else:
            not_wrong_place_count = not_wrong_place_count + 1
            if not_wrong_place_count == 1:
                mc.send_pwm(12,0)
                mc.send_pwm(13,0)   
            wrong_place_count = 0

        if deltax < 5 and not in_wrong_place([x[0],x[3]]):
            draw_marker_direction3(color_arr,[xm1[0],xm1[3]], [x[0],x[3]])  #予測の方向の直線
            draw_point(color_arr, x[0], x[3])
            draw_point(color_arr, xm1[0], xm1[3])
            distance = distance_from_line2((tools[0].pos),[x[0],x[3]],[xm1[0],xm1[3]])
            distance2 = distance_from_line2((tools[1].pos),[x[0],x[3]],[xm1[0],xm1[3]])
            if blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and (blackrubber_count < 6 and yellowtube_count < 2 and 513 > x[3]):
                search_goal(line_in_goal(distance) or line_in_goal(distance2))
            elif blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count < 6 and yellowtube_count == 2 and 513 > x[3]:
                search_goal(line_in_goal(distance))
            elif blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count == 6 and yellowtube_count < 2 and 513 > x[3]:
                search_goal(line_in_goal(distance2))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count < 6 and yellowtube_count < 2:
                if in_black([x[0],x[3]]) or in_yellow([x[0],x[3]]):
                    mc.send_pwm(13,100)
                    mc.send_pwm(12,100)
                else:
                    mc.send_pwm(13,0)
                    mc.send_pwm(12,0)
                search_object(dot_in_bar([x[0],x[3]]))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count < 6 and yellowtube_count == 2:
                if in_black([x[0],x[3]]):
                    mc.send_pwm(13,100)
                    mc.send_pwm(12,100)
                else:
                    mc.send_pwm(13,0)
                    mc.send_pwm(12,0)
                search_object(dot_in_bar([x[0],x[3]]))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count == 6 and yellowtube_count < 2:
                if in_yellow([x[0],x[3]]):
                    mc.send_pwm(13,100)
                    mc.send_pwm(12,100)
                else:
                    mc.send_pwm(13,0)
                    mc.send_pwm(12,0)
                search_object(dot_in_bar([x[0],x[3]]))
            elif blackrubber_count == 6 and yellowtube_count == 2:
                search_object(dot_in_line([x[0],x[3]]))
                    
            else:
                mc.send_pwm(0,0)
            for i in [1,2,4,5]:
                x[i]  = 0
                xm1[i] = 0

        elif deltax >= 5 and not in_wrong_place([x[0],x[3]]):
            draw_prediction(color_arr,h_pred3) #予測場所を点で表示
            draw_prediction(color_arr,h_pred3_1)   #予測場所を点で表示
            draw_marker_direction3(color_arr,[h_pred3_1[0],h_pred3_1[3]], [h_pred3[0],h_pred3[3]])
            distance = distance_from_line2((tools[0].pos),[h_pred3_1[0],h_pred3_1[3]],[h_pred3[0],h_pred3[3]])
            distance2 = distance_from_line2((tools[1].pos),[h_pred3_1[0],h_pred3_1[3]],[h_pred3[0],h_pred3[3]])
            if blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and (blackrubber_count < 6 and yellowtube_count < 2 and 513 > x[3]):
                search_goal(line_in_goal(distance) or line_in_goal(distance2))
            elif blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count < 6 and yellowtube_count == 2 and 513 > x[3]:
                search_goal(line_in_goal(distance))
            elif blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count == 6 and yellowtube_count < 2 and 513 > x[3]:
                search_goal(line_in_goal(distance2))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count < 6 and yellowtube_count < 2:
                if in_black([x[0],x[3]]) or in_yellow([x[0],x[3]]):
                    mc.send_pwm(13,100)
                    mc.send_pwm(12,100)
                else:
                    mc.send_pwm(13,0)
                    mc.send_pwm(12,0)
                search_object(dot_in_bar([h_pred3[0],h_pred3[3]]))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count < 6 and yellowtube_count == 2:
                if in_black([x[0],x[3]]):
                    mc.send_pwm(13,100)
                    mc.send_pwm(12,100)
                else:
                    mc.send_pwm(13,0)
                    mc.send_pwm(12,0)
                search_object(dot_in_bar([h_pred3[0],h_pred3[3]]))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count == 6 and yellowtube_count < 2:
                if in_yellow([x[0],x[3]]):
                    mc.send_pwm(13,100)
                    mc.send_pwm(12,100)
                else:
                    mc.send_pwm(13,0)
                    mc.send_pwm(12,0)
                search_object(dot_in_bar([h_pred3[0],h_pred3[3]]))            
            elif blackrubber_count == 6 and yellowtube_count == 2:
                search_object(dot_in_line([h_pred3[0],h_pred3[3]]))
            else:
                mc.send_pwm(0,0)
                
            #search_object(line_in_object2(object_polygon, [h_pred3_1[0],h_pred3_1[3]], [h_pred3[0],h_pred3[3]]))
        
        if blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count < 6:
            if in_black([x[0],x[3]]):
                blackrubber_count = blackrubber_count + 1
        elif blackrubber_count % 2 == 1:
            if out_black([x[0],x[3]]):
                blackrubber_count = blackrubber_count + 1

        if yellowtube_count % 2 == 0 and blackrubber_count % 2 == 0 and yellowtube_count < 2:
            if in_yellow([x[0],x[3]]):
                yellowtube_count = yellowtube_count + 1
        elif yellowtube_count % 2 == 1:
            if out_yellow([x[0],x[3]]):
                yellowtube_count = yellowtube_count + 1

        print(blackrubber_count, yellowtube_count)
        
        draw_time = draw_hand2(color_arr, x, hand)
        delta_t = draw_time - previous_time
        #print(delta_t)
        previous_time = draw_time
        draw_goals(color_arr)
        flag = draw(color_arr)
        #print(np_hand2)
        #print(np_hand2[0])
        # a = np.squeeze(np_hand)
        #print(a[:,0])
        # print(np_hand)
    out.release()

    mc.valve(0,0)
    mc.valve(1,0)
    mc.valve(2,0)
    mc.comp_stop()
    mc.allmotor_stop()

    traj = np.array(trajectory.trajectory)
    #print(traj)
    directory_path = "/home/toyoshima/script/hand_detection/exp_module/traj_time"
    file_name = f"traj_time_{now.strftime('%Y%m%d_%H%M%S')}.npy"
    full_path = os.path.join(directory_path, file_name)
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

def draw_hand2(color_arr, x, hand):  
    cv2.drawContours(      #緑で手の輪郭を描画
        color_arr,
        hand.contour,
        -1,
        color=(0, 255, 0))

    cv2.circle(            #緑で手の重心を描画
        color_arr,
        (int(x[0]), int(x[3])),
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
        if key == ord("t"):
            mc.send_pwm(12,100)
            mc.send_pwm(13,100)
        elif key == ord("y"):
            mc.send_pwm(12,0)
            mc.send_pwm(13,0)            
        return True

def draw_goals(img):
    for t in tools:
        t.draw(
            img,
            color=(255, 0, 0)
        )

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
    
def draw_marker2(img, xm1, marker):
    cv2.drawContours(      #青でマーカーの輪郭を描画
        img,
        marker.contour,
        -1,
        color=(255, 0, 0))

    cv2.circle(            #青でマーカーの重心を描画
        img,
        (int(xm1[0]), int(xm1[3])),
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

def dot_in_object(contour, pt):
    #return cv2.pointPolygonTest(contour, pt, False) 
    x = int(pt[0]) 
    if contour[0][0] < x < contour[3][0]:
        return 1
    elif contour[0][0] == x or x == contour[3][0]:
        return 0
    else:
        return -1
    
def dot_in_line(pt):
    x = int(pt[0])
    y = int(pt[1])
    if (line1_pt1[0] -5  <= x <= line1_pt2[0] +5 or line2_pt1[0] -5 <= x <= line2_pt2[0] +5
        or line3_pt1[0] -5 <= x <= line3_pt2[0] +5 or line4_pt1[0] -5<= x <= line4_pt2[0] +5):
        return 1
    else:
        return -1
    
def dot_in_bar(pt):
    x = int(pt[0])
    y = int(pt[1])
    if (bar1_pt1[1] -5 <= y <= bar1_pt2[1] +5 or bar2_pt1[1] -5 <= y <= bar2_pt2[1] +5
        or bar3_pt1[1] -5 <= y <= bar3_pt2[1] +5):
        return 1
    else:
        return -1

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
            if  polygon[0][0] < x < polygon[3][0] and polygon[0][1] < y < polygon[3][1]:
                question = 1
                return question
        return question
    
def distance_from_line(query_point, c0, c1):
    # 直線を構成する2点の座標
    x1 = int(c0[0]) 
    y1 = int(c0[1])
    x2 = int(c1[0])
    y2 = int(c1[1])

    # 点の座標
    #x0, y0 = query_point
    x0 = int(query_point[0])
    y0 = int(query_point[1])

    # 直線の方程式の係数 (ax + by + c = 0)
    a = y2 - y1
    b = x1 - x2
    c = (x2 * y1) - (x1 * y2)

    # 直線と点の距離を計算
    numerator = abs(a * x0 + b * y0 + c)
    denominator = math.sqrt(a**2 + b**2)
    distance = numerator / denominator

    return distance

def distance_from_line2(query_point, c0, c1):
    # 直線を構成する2点の座標
    x1 = int(c0[0]) 
    y1 = int(c0[1])
    x2 = int(c1[0])
    y2 = int(c1[1])

    # 点の座標
    #x0, y0 = query_point
    x0 = int(query_point[0])
    y0 = int(query_point[1])

    if x2 == x1:
        distance = abs(x0 - x1)

    # 直線の方程式の係数 (ax + by + c = 0)
    else:
        a = y2 - y1
        b = x1 - x2
        c = (x2 * y1) - (x1 * y2)

        # 直線と点の距離を計算
        numerator = abs(a * x0 + b * y0 + c)
        denominator = math.sqrt(a**2 + b**2)
        distance = numerator / denominator

    return distance

def line_in_goal(distance):
    if radius >= distance:
        return True
    else:
        return False
    
def search_goal(zeroone):
    if zeroone:
        mc.send_pwm(0,100)
    else:
        mc.send_pwm(0,0)


# tools = [
#     Goal(695, 215, radius), 
#     Goal(880, 215, radius)
# ]


def in_black(pos):
    if 655 < pos[0] < 735 and 175 < pos[1] < 255:
        return True

def out_black(pos):
    if 513 < pos[1] < 612:
        return True

def in_yellow(pos):
    if 840 < pos[0] < 920 and 175 < pos[1] < 255:
        return True

def out_yellow(pos):
    if 513 < pos[1] < 612:
        return True
    
def in_wrong_place(pos):
    if (561 < pos[0] < 642 and 175 < pos[1] < 255) or (752 < pos[0] < 827 and 175 < pos[1] < 255):
        return True
    else:
        return False

def draw_imaginary_object(img):
    cv2.rectangle(
        img,
        (655,175),
        (735,255),
        color=(0, 255, 0),
        thickness=2
    )

    cv2.rectangle(
        img,
        (840,175),
        (920,255),
        color=(0, 255, 0),
        thickness=2
    )

    cv2.rectangle(
        img,
        (561,175),
        (642,255),
        color=(0, 255, 0),
        thickness=2
    )

    cv2.rectangle(
        img,
        (752,175),
        (827,255),
        color=(0, 255, 0),
        thickness=2
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