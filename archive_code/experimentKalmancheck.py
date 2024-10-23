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
#import motor_controller3 as mc
from motor_controller import MotorController 
import matplotlib.pyplot as plt
import hand_detection.z_trajectory as tr
import hand_detection.kalmanfilter as klf
#import kalmanfilteronesetstop as klf

num_time = 3

min_th_h = None
max_th_h = None
min_th_m = None
max_th_m = None
min_th_o = None
max_th_o = None
mask = None
manager = None
trajectory = None
trajectory_points = []
trajectory_estimate = []
trajectory_predict = [[0, 0],[0,0],[0,0]]
radius = 40
motor_power = 200
begin_time = None

prob = 0.15

last_time = time.time()
data = []
mc = MotorController()

object_width = 95
object_height = 40
#object_pt1 = (595, 200)
x1 = random.randint(300, 805)
y1 = 200
object_pt1 = (x1, y1)
x2 = x1 + object_width
y2 = y1 + object_height
object_pt2 = (x2, y2)
#object_polygon = np.array([[595, 200], [595, 240], [690, 200], [690, 240]])
object_polygon = np.array([[x1, y1], [x1, y2], [x2, y1], [x2, y2]])
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
draw_time = None

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
    return md.load_hs_threshold("marker_threshold4")



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
    T=[]
    dt = 0.1
    t = 0
    
    target = tools[r]
    flag = True

    hand = Hand(min_th_h, max_th_h, mask)
    marker = Marker(min_th_m, max_th_m, mask)
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
    previous_previous_x = 0
    previous_x = 0
    while flag:
        color_arr = get_color_arr()  #kinectから色情報（配列）を取得
        # hand = get_hand(color_arr)   #色情報から手の輪郭を取得
        hand.update(color_arr)
        marker.update(color_arr)
        object.update(color_arr)
        center = marker.compute_center()
        #trajectory.push_point(hand.center, time.time() - begin_time) 
        trajectory_points.append(np.array(hand.center))
        if previous_previous_x is not None:
            previous_previous_x = previous_x
        previous_x = x[0]
        x, P, h_pred3 = klf.kalman_filter(x, P, np.array(hand.center))
        xm1, Pm1, h_pred3_1 = klf.kalman_filter(xm1, Pm1, np.array(center))

        deltax = abs(previous_x - x[0])
        print(x[0])
        print(deltax)
        deltadeltax = abs(previous_previous_x - x[0])
        
        trajectory_estimate.append(x)
        #trajectory_predict.append(h_pred3)
        # points.append(hand.center)   #手の重心の座標をリストに追加　繰り返して軌跡に

        #draw_direction(color_arr,a,b, hand.center)
        #print(x)
        #print(hand.center)
        
        draw_marker(color_arr, marker)
        draw_marker_direction2(color_arr,center, hand.center)  #予測していない手の方向
        #draw_imaginary_object(color_arr)
        draw_imaginary_line(color_arr, line1_pt1, line1_pt2)
        draw_imaginary_line(color_arr, line2_pt1, line2_pt2)
        draw_imaginary_line(color_arr, line3_pt1, line3_pt2)
        draw_imaginary_line(color_arr, line4_pt1, line4_pt2)
        draw_imaginary_line(color_arr, bar1_pt1, bar1_pt2)
        draw_imaginary_line(color_arr, bar2_pt1, bar2_pt2)
        draw_imaginary_line(color_arr, bar3_pt1, bar3_pt2)
        #if deltax < 10 and deltadeltax <10:
        if deltax < 5:
            draw_marker_direction3(color_arr,[center[0],h_pred3_1[3]], [hand.center[0],h_pred3[3]])  #予測の方向の直線
            draw_point(color_arr, hand.center[0], h_pred3[3])
            draw_point(color_arr, center[0], h_pred3_1[3])
            trajectory_predict.append([hand.center[0],h_pred3[3]])
            #search_object(dot_in_object(line2_polygon,[hand.center[0],0]))
            search_object(dot_in_line([hand.center[0],h_pred3[3]]))
            for i in [1,2]:
                x[i]  = 0
                xm1[i] = 0

    


        else:
            draw_prediction(color_arr,h_pred3) #予測場所を点で表示
            draw_prediction(color_arr,h_pred3_1)   #予測場所を点で表示
            draw_marker_direction3(color_arr,[h_pred3_1[0],h_pred3_1[3]], [h_pred3[0],h_pred3[3]])
            trajectory_predict.append([h_pred3[0],h_pred3[3]])
            #search_object(dot_in_object(line2_polygon,h_pred3))
            search_object(dot_in_line([h_pred3[0],h_pred3[3]]))
        
        #draw_prediction(color_arr,h_pred3_1)   #予測場所を点で表示
        #draw_imaginary_object2(color_arr)
        #search_object(dot_in_object(line1_polygon,h_pred3))
        
        #draw_object(color_arr,object)
        #np_object = np.array(object.contour)
        #np_object2 = np.squeeze(np_object)
        #search_object(line_in_object2(object_polygon, center0, center1))
        #部品サーチ未来
        #search_object(line_in_object2(object_polygon, [h_pred3_1[0],h_pred3_1[3]], [h_pred3[0],h_pred3[3]]))
        
        #print(line_in_object2(object_polygon, [h_pred3_1[0],h_pred3_1[3]], [h_pred3[0],h_pred3[3]]))
        #wall(hand)
        #guide2(hand, target)
        #print(h_pred3)
        draw_time = draw_hand(color_arr, hand)
        delta_t = draw_time - previous_time
        #print(delta_t)
        previous_time = draw_time
        flag = draw(color_arr, target)
        #print(np_hand2)
        #print(np_hand2[0])
        # a = np.squeeze(np_hand)
        #print(a[:,0])
        # print(np_hand)
        t=t+dt
        T.append(t)

    

    T.append(t+dt)
    T.append(t+dt)
    T.append(t+dt)
    trajectory_estimate.append(x)
    trajectory_estimate.append(x)
    trajectory_estimate.append(x)

    #print(trajectory_points)
    observation = np.array(trajectory_points)
    observation = np.vstack([observation, np.array([0, 0])])
    observation = np.vstack([observation, np.array([0, 0])])
    observation = np.vstack([observation, np.array([0, 0])])
    #print(type([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [6, 8],[6,9],[5,10],[4,11],[3,12],[2,13], [1, 14],[0,15],[-1,16],[-2,17],[-1,17],[1,17],[3,17],[5,17],[7,17],[9,17],[11,17],[13,17]]))

    #measurements = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [6, 8],[6,9],[5,10],[4,11],[3,12],[2,13], [1, 14],[0,15],[-1,16],[-2,17],[-1,17],[1,17],[3,17],[5,17],[7,17],[9,17],[11,17],[13,17]])
    #print(measurements[:,0])
    #print(trajectory_predict)
    tp = np.array(trajectory_predict)
    te = np.array(trajectory_estimate)
    #print(tp)
    #print(tp[:,0])
    '''print(type(trajectory.trajectory))
    traj = np.array(trajectory.trajectory)
    print((type(traj)))
    points = [item[0] for item in traj]
    times = [item[1] for item in traj]
    print(points)
    #print(times)
    points_x = [item[0] for item in points]
    points_y = [item[1] for item in points]
    print(points_x)
    print(points_y)
    zahyou = [list(e) for e in zip(points_x, points_y)]
    print(zahyou)'''


    plt.plot(T,te[:,0], 'o', color='red', linewidth=1.0, label='Estimation')
    plt.plot(T,observation[:, 0], '*',color='green',label='Obvervation')
    plt.plot(T,tp[:,0], '*',color='blue',label='Prediction')
    # plt.errorbar(T,XT, yerr=XTERR, capsize=5, fmt='o', color='red', ecolor='orange',label='Estimate')
    plt.xlabel('T')
    plt.ylabel('X')
    plt.grid(True)
    plt.legend()
    plt.show()

       
        
        




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
        
def draw(color_arr, target):
    #draw_goals(color_arr, target)
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
    
def draw_imaginary_object(img):
    cv2.rectangle(
        img,
        object_pt1,
        object_pt2,
        color=(0, 255, 0),
        thickness=2
    )

def draw_imaginary_line(img, line_pt1, line_pt2):
    cv2.rectangle(
        img,
        line_pt1,
        line_pt2,
        color=(255, 0, 0),
        thickness=-1
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
    '''if (line1_pt1[0] <= x <= line1_pt2[0] or line2_pt1[0] <= x <= line2_pt2[0] 
        or line3_pt1[0] <= x <= line3_pt2[0] or line4_pt1[0] <= x <= line4_pt2[0]
        or bar1_pt1[1] <= y <= bar1_pt2[1] or bar2_pt1[1] <= y <= bar2_pt2[1]
        or bar3_pt1[1] <= y <= bar3_pt2[1]):'''
    if (bar1_pt1[1] -5<= y <= bar1_pt2[1] +5
        or bar3_pt1[1] - 5 <= y <= bar3_pt2[1] + 5):
        return 1
    elif bar2_pt1[1] -5<= y <= bar2_pt2[1] +5:
        return 0
    else:
        return -1
    

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





def init():
    global mask, min_th_h, max_th_h, min_th_m, max_th_m, manager, begin_time
    mask = load_mask2()
    (min_th_h, max_th_h) = load_threshold_h()
    (min_th_m, max_th_m) = load_threshold_m()
    begin_time = time.time()
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
    
