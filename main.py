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
from hand import Hand
from marker import Marker
from module_controller import ModuleController 
from trajectory import Trajectory
import kalmanfilter as klf
import math
import random
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

radius = 75


begin_time = None

frame_width = int(1280)
frame_height = int(720)
fps = float(11)

last_time = time.time()
data = []
mc = ModuleController()


#以下仮想的な振動する溝　縦がline横線がbar
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

class Goal:    #4つの棚に配置する丸(正しい部品があるときに丸を表示)
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
    

def load_coordinates(file_name):
    file_path = os.path.join(os.path.dirname(__file__), "coordinates_file", f"{file_name}.txt")
    coordinates_arr = np.loadtxt(file_path)
    return coordinates_arr




tools = []    #正しい部品がある棚を格納
wrong_tools = []  #間違った部品がある棚を格納

shelves_coordinates= load_coordinates("shelves_coordinates")

heights = shelves_coordinates[:, 2]   # 棚の高さ
widths = shelves_coordinates[:, 3]    # 棚の横幅
centers = shelves_coordinates[:, 0:2].astype(int)  # 各棚の中心 (x, y)

# blackゴム足の2つの棚をランダムに1つを正解の棚にもう1つを間違いの棚にする
if random.randint(0, 1) == 0:
    true_index = 0
    wrong_index = 1
else:
    true_index = 1
    wrong_index = 0

tools.append(Goal(centers[true_index][0], centers[true_index][1], radius, heights[true_index], widths[true_index])) # black
wrong_tools.append(Goal(centers[wrong_index][0], centers[wrong_index][1], radius, heights[wrong_index], widths[wrong_index])) # wrong black

# yellowチューブの2つの棚をランダムに1つを正解の棚にもう1つを間違いの棚にする
if random.randint(0, 1) == 0:
    true_index = 2
    wrong_index = 3
else:
    true_index = 3
    wrong_index = 2

tools.append(Goal(centers[true_index][0], centers[true_index][1], radius, heights[true_index], widths[true_index])) # yellow
wrong_tools.append(Goal(centers[wrong_index][0], centers[wrong_index][1], radius, heights[wrong_index], widths[wrong_index])) # wrong yellow

# # 正解の棚を固定する．どちらも左側が正解の棚
# tools.extend([Goal(centers[0][0], centers[0][1], radius, heights[0], widths[0]), Goal(centers[2][0], centers[2][1], radius, heights[2], widths[2])])
# wrong_tools.extend([Goal(centers[1][0], centers[1][1], radius, heights[1], widths[1]), Goal(centers[3][0], centers[3][1], radius, heights[3], widths[3])])


class State:   #使ってない
    assem = None
    target = None
    
    def __init__(self, assem, target):
        self.assem = assem
        self.target = target


def load_mask():   #カメラの画角のうち画像認識するのは緑の作業台だけでいいのでそこ以外を切り取るため(画像(mask.png)を使ってやる方法)
    mask = Image.open("/home/toyoshima/script/hand_detection/mask.png")
    # mask = Image.open("mask.png")
    return np.asarray(mask)

def load_mask_hand():     #同上(具体的に座標を与えて切り取るやり方)ピンクの手袋用
    mask = np.zeros((720,1280))
    for i in range(285, 915):
        for j in range(173, 612):
            mask[j][i] = 1
    return mask

def load_mask_marker():     #同上(具体的に座標を与えて切り取るやり方)黄色いマーカー用
    mask = np.zeros((720,1280))
    for i in range(285, 915):
        for j in range(255, 612):
            mask[j][i] = 1
    return mask

def load_threshold_h():    #ピンクの手袋を認識するためのしきい値をロード　(ロードするファイルは4つ数字が書いてあり，左上;hueの下限　左下;hueの上限　右上;hueの下限　右下;hueの上限)
    return Hand.load_hs_threshold("hand_threshold")

def load_threshold_m():
    return Marker.load_hs_threshold("marker_threshold")   #上のマーカー版




def kinect_color():
    kinect = Kinect()
    def get_color():
        kinect.update()
        return kinect.color_arr

    return get_color


get_color_arr = kinect_color()           

def search_object(in_out):   #溝振動用
    if in_out == 1:
        mc.send_pwm(0,100)
    elif in_out == 0:
        mc.send_pwm(0,100)
    else:
        mc.send_pwm(0,0)
       

def toward_tool():
    now = datetime.datetime.now()

    tar_name = 'kobayashi'  #被験者の名前を入れる
    base_dir = f'/home/toyoshima/script/kobayashi/data/{tar_name}'
    directory_path_v = os.path.join(base_dir, 'kinect_movie')
    directory_path_t = os.path.join(base_dir, "trajectory")
    directory_path_g = os.path.join(base_dir, "goaltime")

    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(directory_path_t, exist_ok=True)
    os.makedirs(directory_path_v, exist_ok=True)
    os.makedirs(directory_path_g, exist_ok=True)

    dir_length = len(glob(os.path.join(directory_path_v, '*')))

    # dir_length_t = len(glob(os.path.join(directory_path_t, '*')))
    file_name_t = f"trajectory_{now.strftime('%Y%m%d_%H%M%S')}_{dir_length}.csv"
    full_path_t = os.path.join(directory_path_t, file_name_t)

    file_name_g = f"goaltime_{now.strftime('%Y%m%d_%H%M%S')}_{dir_length}.csv"
    full_path_g = os.path.join(directory_path_g, file_name_g)

    file_name_v = f"kinect_movie_{now.strftime('%Y%m%d_%H%M%S')}_{dir_length}.mp4"
    full_path_v = os.path.join(directory_path_v, file_name_v)
    #output_file = "output_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(full_path_v, fourcc, fps, (frame_width, frame_height), True)

    #上は動画と手の軌跡を保存している
    
    blackrubber = tools[0]
    yellowtube = tools[1]
    wrong_goals = wrong_tools

    flag = True
    blackrubber_count = 0    #正しいゴム足の棚に手を入れると+1,その後作業台手前に手が入ると+1   (偶数で部品を手に取ろうとしている段階，奇数で部品を手にとって手前に戻す段階)
    yellowtube_count = 0
    hand = Hand(min_th_h, max_th_h, mask)
    marker = Marker(min_th_m, max_th_m, mask2)



    trajectory = Trajectory(1280, 720)    #軌跡を保存する

    x = np.array([0, 0, 0, 0, 0, 0])
    xm1 = np.array([0, 0, 0, 0, 0, 0])
    P = np.eye(6)
    Pm1 = np.eye(6)
    previous_previous_x = [0,0]
    previous_x = [0,0]
    time.sleep(1)
    mc.comp_start()
    mc.mod(1)
    mc.valve(0,1)
    mc.valve(1,1)
    mc.valve(2,1)
    mc.pressure(200)
    begin_time = time.time()
    six_two_count = 0
    wrong_place_count = 0
    not_wrong_place_count = 0
    while flag:
        color_arr = get_color_arr()  #kinectから色情報（配列）を取得
        

        hand.update(color_arr)
        marker.update(color_arr)
        center = marker.compute_center()
        trajectory.push_point([x[0],x[3]], time.time() - begin_time)    #手の重心の座標と経過時間をリストに追加

        if previous_previous_x is not None:
            previous_previous_x = previous_x
        previous_x = x
        x, P, h_pred3 = klf.kalman_filter(x, P, np.array(hand.center))    #手の重心のカルマンフィルタの更新　x;手の重心にカルマンフィルタかけたもの　pred3;手の重心の予測位置
        xm1, Pm1, h_pred3_1 = klf.kalman_filter(xm1, Pm1, np.array(center))  #マーカーのカルマンフィルタの更新　x;マーカーにカルマンフィルタかけたもの　pred3;マーカーの重心の予測位置

        deltax = math.sqrt((previous_x[0] - x[0])**2 + (previous_x[3] - x[3])**2)   #前ループでの手の重心の座標からどれだけ離れたか

        
        draw_marker(color_arr, xm1, marker)     #予測なしマーカー描画
        draw_marker_direction(color_arr,[xm1[0],xm1[3]], [x[0],x[3]])  #予測なし手の方向描画
        
        draw_imaginary_object(color_arr, shelves_coordinates)   #棚を四角で区切る
        draw_imaginary_line(color_arr, bar1_pt1, bar1_pt2)    #横溝3本
        draw_imaginary_line(color_arr, bar2_pt1, bar2_pt2)
        draw_imaginary_line(color_arr, bar3_pt1, bar3_pt2)
        

        '''これ以降の条件分岐は部品を4つ習得するフェーズにおいて,部品を棚に取りに行くときには手の方向と正しい棚が交わったときにモータ0が振動,手が正しい棚に入ったときに
            モータ10と14が連続的に振動，間違ったときに断続的に振動，取って手前に部品を起きに行くときは横向きの溝で振動　　　を部品をてまえに4つ揃えるまで行っている
        '''
        
        if blackrubber_count == 6 and yellowtube_count == 2:    #ゴム足3つとチューブ1つを取った状態     マルチスレッドにして経過時間でvalveonにしたほうがいい
            six_two_count = six_two_count + 1         #
        if six_two_count == 1:    #valveをoffにしてカフを緩める
           mc.valve(0,0)
           mc.valve(1,0)
           mc.valve(2,0)
        if six_two_count == 10:    #valveをonにして締める
           mc.valve(0,1)
           mc.valve(1,1) 
           mc.valve(2,1)       

        if in_wrong_place([x[0],x[3]], wrong_goals):   #間違った部品棚に手が入ったときに断続的振動　　マルチスレッドにして経過時間でsend_pwmの強さを切り替えたほうがいい
            wrong_place_count = wrong_place_count + 1
            not_wrong_place_count = 0
            if wrong_place_count % 4 == 1:
                mc.send_pwm(14,100)
                mc.send_pwm(10,100)
            elif wrong_place_count % 4 == 3:
                mc.send_pwm(14,0)
                mc.send_pwm(10,0)                
        else:
            not_wrong_place_count = not_wrong_place_count + 1
            if not_wrong_place_count == 1:
                mc.send_pwm(14,0)
                mc.send_pwm(10,0)   
            wrong_place_count = 0

        if deltax < 5 and not in_wrong_place([x[0],x[3]], wrong_goals):      #前回ループから手の進んだ距離が5未満ならカルマンフィルタによる予測位置を使わない
            draw_marker_direction3(color_arr,[xm1[0],xm1[3]], [x[0],x[3]])  #予測の方向の直線
            draw_point(color_arr, x[0], x[3])    #予測なし手の重心描画
            draw_point(color_arr, xm1[0], xm1[3])  #予測なしマーカーの重心描画
            distance = distance_from_line2((tools[0].pos),[x[0],x[3]],[xm1[0],xm1[3]])   #正しいゴム足の棚の中心と手の方向を示す直線の距離
            distance2 = distance_from_line2((tools[1].pos),[x[0],x[3]],[xm1[0],xm1[3]])   #正しいゴム足の棚の中心と手の方向を示す直線の距離
            if blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and (blackrubber_count < 6 and yellowtube_count < 2 and 513 > x[3]):  #部品を取るフェーズかつチューブもゴム足も残っているかつ手のy座標が部品を置く位置の外
                search_goal(line_in_goal(distance) or line_in_goal(distance2))     #手の方向がどちらかの正しい部品の棚に入っているときに振動
            elif blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count < 6 and yellowtube_count == 2 and 513 > x[3]:   #部品を取るフェーズかつゴム足はまだ残っているかつ手のy座標が部品を置く位置の外
                search_goal(line_in_goal(distance))     #手の方向が正しいゴム足の棚に入っているときに振動
            elif blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count == 6 and yellowtube_count < 2 and 513 > x[3]:    #部品を取るフェーズかつtチューブはまだ残っているかつ手のy座標が部品を置く位置の外
                search_goal(line_in_goal(distance2))     #手の方向が正しいチューブの棚に入っているときに振動
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count < 6 and yellowtube_count < 2:     #手に取った部品を手前に持ってくるフェーズかつチューブもゴム足も残っている
                if in_black([x[0],x[3]], blackrubber.h_min, blackrubber.h_max, blackrubber.w_min, blackrubber.w_max) or in_yellow([x[0],x[3]], yellowtube.h_min, yellowtube.h_max, yellowtube.w_min, yellowtube.w_max):   #正しい部品の棚に田が入っているとき連続的に振動
                    mc.send_pwm(10,100)
                    mc.send_pwm(14,100)
                else:
                    mc.send_pwm(10,0)
                    mc.send_pwm(14,0)
                search_object(dot_in_bar([x[0],x[3]]))    #溝による振動
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count < 6 and yellowtube_count == 2:     #手に取った部品を手前に持ってくるフェーズかつゴム足が残っている
                if in_black([x[0],x[3]], blackrubber.h_min, blackrubber.h_max, blackrubber.w_min, blackrubber.w_max):
                    mc.send_pwm(10,100)
                    mc.send_pwm(14,100)
                else:
                    mc.send_pwm(10,0)
                    mc.send_pwm(14,0)
                search_object(dot_in_bar([x[0],x[3]]))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count == 6 and yellowtube_count < 2:     #手に取った部品を手前に持ってくるフェーズかつチューブが残っている
                if in_yellow([x[0],x[3]], yellowtube.h_min, yellowtube.h_max, yellowtube.w_min, yellowtube.w_max):
                    mc.send_pwm(10,100)
                    mc.send_pwm(14,100)
                else:
                    mc.send_pwm(10,0)
                    mc.send_pwm(14,0)
                search_object(dot_in_bar([x[0],x[3]]))
            elif blackrubber_count == 6 and yellowtube_count == 2:
                search_object(dot_in_line([x[0],x[3]]))
                    
            else:
                mc.send_pwm(0,0)

            for i in [1,2,4,5]:   #手の移動速度が低い場合なので，移動距離が5未満のときはカルマンフィルタの速度，加速度成分は0に毎回更新している
                x[i]  = 0
                xm1[i] = 0

        elif deltax >= 5 and not in_wrong_place([x[0],x[3]], wrong_goals):      #カルマンフィルタによる予測座標を使う場合
            draw_prediction(color_arr,h_pred3) #予測場所を点で表示
            draw_prediction(color_arr,h_pred3_1)   #予測場所を点で表示
            draw_marker_direction3(color_arr,[h_pred3_1[0],h_pred3_1[3]], [h_pred3[0],h_pred3[3]])    #予測した手の方向
            distance = distance_from_line2((tools[0].pos),[h_pred3_1[0],h_pred3_1[3]],[h_pred3[0],h_pred3[3]])     #予測した手の方向と正しい棚の中心の距離
            distance2 = distance_from_line2((tools[1].pos),[h_pred3_1[0],h_pred3_1[3]],[h_pred3[0],h_pred3[3]])
            if blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and (blackrubber_count < 6 and yellowtube_count < 2 and 513 > x[3]):
                search_goal(line_in_goal(distance) or line_in_goal(distance2))
            elif blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count < 6 and yellowtube_count == 2 and 513 > x[3]:
                search_goal(line_in_goal(distance))
            elif blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count == 6 and yellowtube_count < 2 and 513 > x[3]:
                search_goal(line_in_goal(distance2))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count < 6 and yellowtube_count < 2:
                if in_black([x[0],x[3]], blackrubber.h_min, blackrubber.h_max, blackrubber.w_min, blackrubber.w_max) or in_yellow([x[0],x[3]], yellowtube.h_min, yellowtube.h_max, yellowtube.w_min, yellowtube.w_max):
                    mc.send_pwm(10,100)
                    mc.send_pwm(14,100)
                else:
                    mc.send_pwm(10,0)
                    mc.send_pwm(14,0)
                search_object(dot_in_bar([h_pred3[0],h_pred3[3]]))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count < 6 and yellowtube_count == 2:
                if in_black([x[0],x[3]], blackrubber.h_min, blackrubber.h_max, blackrubber.w_min, blackrubber.w_max):
                    mc.send_pwm(10,100)
                    mc.send_pwm(14,100)
                else:
                    mc.send_pwm(10,0)
                    mc.send_pwm(14,0)
                search_object(dot_in_bar([h_pred3[0],h_pred3[3]]))
            elif (blackrubber_count % 2 == 1 or yellowtube_count % 2 == 1) and blackrubber_count == 6 and yellowtube_count < 2:
                if in_yellow([x[0],x[3]], yellowtube.h_min, yellowtube.h_max, yellowtube.w_min, yellowtube.w_max):
                    mc.send_pwm(10,100)
                    mc.send_pwm(14,100)
                else:
                    mc.send_pwm(10,0)
                    mc.send_pwm(14,0)
                search_object(dot_in_bar([h_pred3[0],h_pred3[3]]))            
            elif blackrubber_count == 6 and yellowtube_count == 2:
                search_object(dot_in_line([h_pred3[0],h_pred3[3]]))
            else:
                mc.send_pwm(0,0)
                

        #以下は部品を何個取得しているか，取るフェーズなのか手前に持ってくるフェーズなのかを番号で管理　　
        
        if blackrubber_count % 2 == 0 and yellowtube_count % 2 == 0 and blackrubber_count < 6:
            if in_black([x[0],x[3]], blackrubber.h_min, blackrubber.h_max, blackrubber.w_min, blackrubber.w_max):
                blackrubber_count = blackrubber_count + 1
                trajectory.push_goal([x[0],x[3]], time.time() - begin_time)
        elif blackrubber_count % 2 == 1:
            if out_black([x[0],x[3]]):
                blackrubber_count = blackrubber_count + 1


        if yellowtube_count % 2 == 0 and blackrubber_count % 2 == 0 and yellowtube_count < 2:
            if in_yellow([x[0],x[3]], yellowtube.h_min, yellowtube.h_max, yellowtube.w_min, yellowtube.w_max):
                yellowtube_count = yellowtube_count + 1
                trajectory.push_goal([x[0],x[3]], time.time() - begin_time)
        elif yellowtube_count % 2 == 1:
            if out_yellow([x[0],x[3]]):
                yellowtube_count = yellowtube_count + 1

        if blackrubber_count == 6 and yellowtube_count == 2 :
            trajectory.write_trajectory_to_file(full_path_t)
            trajectory.write_goaltime_to_file(full_path_g)
            finish()

        print(blackrubber_count, yellowtube_count)     #0 0から始まり，手が正しい黒ゴムの棚に入ると1 0その後手前に手を持ってくると2 0最終的にすべて手前に集めると6 2になる
        
        draw_hand2(color_arr, x, hand)
        draw_goals(color_arr)
        flag = draw(color_arr)
        frame = color_arr[:, :, :3]
        out.write(frame)

    out.release()

    mc.valve(0,0)
    mc.valve(1,0)
    mc.valve(2,0)
    mc.comp_stop()
    mc.allmotor_stop()

    traj = np.array(trajectory.trajectory)
    print(traj)

    np.save(full_path_t, traj)


def finish():
    now = datetime.datetime.now()
    # np.savetxt('exp_data/data' + now.strftime('%Y%m%d_%H%M%S') + '.csv', data)
    exit(0)


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
    draw_table(color_arr)
    cv2.imshow("img", color_arr)
    
    key = cv2.waitKey(1)
    if key == ord("q"):
        return False
    else:
        if key == ord("t"):
            mc.send_pwm(14,100)
            mc.send_pwm(10,100)
        elif key == ord("y"):
            mc.send_pwm(14,0)
            mc.send_pwm(10,0)            
        return True

def draw_goals(img):
    for t in tools:
        t.draw(
            img,
            color=(255, 0, 0)
        )

def draw_table(img): #テーブルの輪郭を緑で描写
    table_coordinates=load_coordinates("table_coordinates")
    top_left = (int(table_coordinates[0][0]), int(table_coordinates[0][1]))
    bottom_right = (int(table_coordinates[1][0]), int(table_coordinates[1][1]))
    cv2.rectangle(
        img,
        top_left,
        bottom_right,
        color=(0, 255, 0),
        thickness=2
    )
    
def draw_marker(img, xm1, marker):
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
    cv2.circle(            #赤でマーカーの重心を描画
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

def draw_marker_direction(img, c0, c1):
    x1 = int(c0[0]) 
    y1 = int(c0[1])
    x2 = int(c1[0])
    y2 = int(c1[1])

    height, width, _ = img.shape

    if x2 == x1:
        x_1 = x1
        y_1 = 0
        x_2 = x2
        y_2 = height
    else:  
        a = (y2 - y1)/(x2 - x1)
        b = y1 - a * x1

        x_1 = 0
        y_1 = int(a * x_1 + b)

        x_2 = width
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

    # 直線の方程式の係数 (ax + by + 
    #  = 0)
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


def in_black(pos, h_min, h_max, w_min, w_max):      #手が正しいゴム足の棚に入っているかを判定
    if w_min < pos[0] < w_max and h_min < pos[1] < h_max:
        return True

def out_black(pos, h_min=513, h_max=612):      #手が手前(部品を置く場所)に入っているかを判定
    if h_min < pos[1] < h_max:
        return True

def in_yellow(pos, h_min, h_max, w_min, w_max):      #手が正しいチューブの棚に入っているかを判定
    if w_min < pos[0] < w_max and h_min < pos[1] < h_max:
        return True

def out_yellow(pos, h_min=513, h_max=612):       #手が手前(部品を置く場所)に入っているかを判定
    if h_min < pos[1] < h_max:
        return True
    
def in_wrong_place(pos, wrong_goals):     #手が間違った部品の棚にあるかを判定
    for goal in wrong_goals:
        if (goal.w_min < pos[0] < goal.w_max) and (goal.h_min < pos[1] < goal.h_max):
            return True
    
    return False

def draw_imaginary_object(img, coordinates):
    for center_x, center_y, width, height in coordinates:
        # 左上の座標と右下の座標を計算
        top_left = (int(center_x - width / 2), int(center_y - height / 2))
        bottom_right = (int(center_x + width / 2), int(center_y + height / 2))
        
        # 四角形を描画
        cv2.rectangle(
            img,
            top_left,
            bottom_right,
            color=(0, 255, 0),  # 緑色
            thickness=2
        )


def init():
    global mask, mask2, min_th_h, max_th_h, min_th_m, max_th_m, min_th_o, max_th_o,manager, begin_time
    mask = load_mask_hand()
    mask2 = load_mask_marker()
    (min_th_h, max_th_h) = load_threshold_h()
    (min_th_m, max_th_m) = load_threshold_m()

def main():
    init()
    toward_tool()

if __name__ =="__main__":
    try:
        main()
    # except KeyboardInterrupt:
        # mc.allmotor_stop()
        # mc.comp_stop()
    except Exception as e:
        print(traceback.format_exc())
        print(e)