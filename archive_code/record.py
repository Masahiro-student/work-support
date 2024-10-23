import cv2

import time
# from auto_annotation.plot_images import ImageForPlot, ImagesForPlot
from util.plot_images import ImageForPlot, ImagesForPlot
import numpy as np
from util.custom_capture import CustomCapture
from PIL import Image
import os
import k4a
import time

from util.kinect import Kinect
from util.save_img import FileType, save_img

frame_width = 1280
frame_height = 720
fps = 15
begin_time = time.time()
# VideoWriter を作成する。
output_file = "output_video.mp4"  # 保存する動画ファイル名
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 動画のコーデックを指定

# カラー画像をグレースケールに変換して動画として保存するためisColor=Falseとしています。
out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height), True)

with k4a.Device.open() as device:
    kinect = Kinect(device)
    
    kinect.setup()

    while True:

        with kinect.capture() as capture:
            frame = capture.color.data[:, :, :3]
            print(time.time()-begin_time)
            print(frame.shape)

            # 動画にフレームを書き込む
            out.write(frame)

            cv2.imshow('frame', frame)
            key = cv2.waitKey(10)
            if key == ord('q'):
                break

out.release()