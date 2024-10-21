#不使用

import cv2
import numpy as np
from datetime import datetime
import os

def draw_point(image, point):
    """
    画像に点を描画する関数
    """
    print(point[0])
    cv2.circle(image, (int(point[0]), int(point[1])), 3, (255, 0, 0), -1)

def draw_trajectory(image, trajectory):
    """
    画像に軌跡を描画する関数
    """
    for i in range(1, len(trajectory)):
        cv2.line(image, (int(trajectory[i-1][0]), int(trajectory[i-1][1])), (int(trajectory[i][0]), int(trajectory[i][1])), (0, 140, 255), 2)

def main():
    # 画像の読み込み
    image = cv2.imread("/home/toyoshima/0000.png")
    traj = np.load('/home/toyoshima/trajectory.npy')
    obj = np.load('/home/toyoshima/object_polygon.npy')
    print(obj[0][0])
    print(obj[3][0])
    print(obj[0][1])
    print(obj[3][1])

    '''cv2.rectangle(
        image,
        (453, 200),
        (548, 240),
        color=(0, 255, 0),
        thickness=2
    )'''

    cv2.rectangle(
        image,
        (obj[0][0], obj[0][1]),
        (obj[3][0], obj[3][1]),
        color=(0, 255, 0),
        thickness=2
    )

    # 画像に点を描画
    #for point in traj:
    #    draw_point(image, point)

    # 画像に軌跡を描画
    draw_trajectory(image, traj)

    # 画像を表示
    cv2.imshow("Image with Points and Trajectory", image)
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'saved_image_{current_time}.jpg'

    file_path = os.path.join('/home/toyoshima/script/parts_find', filename)
    cv2.imwrite(file_path, image)

    # 画像を保存
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
