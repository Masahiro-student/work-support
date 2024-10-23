#支援ありの軌跡データのグラフ化のために使用(カルマンフィルタによるノイズ除去なし)

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
#import kalmanfilteronesetstop as klf
import math
import matplotlib

file_path = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_171306_9.npy'

# ファイルを読み込む
traj_time = np.load(file_path)
x = traj_time[:, 0]
y = traj_time[:, 1]
traj = traj_time[:, :2]
T = traj_time[:, 2]






plt.plot(T,y, 'o', color='blue', linewidth=1.0, label='on')
#plt.plot(T,observation[:, 1], '*',color='green',label='Obvervation')
#plt.plot(T,tp[:,3], '*',color='blue',label='Prediction')
# plt.errorbar(T,XT, yerr=XTERR, capsize=5, fmt='o', color='red', ecolor='orange',label='Estimate')
fig = plt.gcf()
canvas = fig.canvas
canvas.set_window_title('kondo_on_0')
plt.xlabel('T')
plt.ylabel('X')
plt.grid(True)
plt.legend()
plt.show()
#plt.savefig('/home/toyoshima/script/hand_detection/raw.jpg')


# 読み込んだデータを表示
