#軌跡データのグラフ化のために使用(カルマンフィルタによるノイズ除去あり)

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
import filtering as klf
#import kalmanfilteronesetstop as klf
import math
import matplotlib

file_path = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_170303_0.npy'

# ファイルを読み込む
traj_time = np.load(file_path)
x = traj_time[:, 0]
y = traj_time[:, 1]
traj = traj_time[:, :2]
measurements = np.delete(traj,0, 0)
T = traj_time[:, 2]
delT=[]
size = T.size
for i in range(1,size):
    delT.append(T[i] - T[i-1])

#print(traj_time)
#print(traj)
#print(measurements)
numdelT = np.array(delT)
#print(numdelT.size)
#print(measurements.shape)

x = np.array([0, 0, 0, 0, 0, 0])
P = np.eye(6)
filtering_x = []
for dt, measurement in zip(numdelT, measurements):
    x, P, _ = klf.kalman_filter(x,P,dt,measurement)
    filtering_x.append([x[0],x[3]])

complete_x = np.array(filtering_x)
print(complete_x)
print(np.delete(T,0, 0))



plt.plot(np.delete(T,0, 0),complete_x[:,1], 'o', color='red', linewidth=1.0, label='Estimation')
#plt.plot(T,observation[:, 1], '*',color='green',label='Obvervation')
#plt.plot(T,tp[:,3], '*',color='blue',label='Prediction')
# plt.errorbar(T,XT, yerr=XTERR, capsize=5, fmt='o', color='red', ecolor='orange',label='Estimate')
plt.xlabel('T')
plt.ylabel('X')
plt.grid(True)
plt.legend()
plt.show()
#plt.savefig('/home/toyoshima/script/hand_detection/raw.jpg')


# 読み込んだデータを表示
