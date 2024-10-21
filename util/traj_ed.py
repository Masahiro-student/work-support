#不使用

import cv2
import numpy as np

def draw_point(image, point):
    """
    画像に点を描画する関数
    """
    print(point[0])
    cv2.circle(image, (point[0], point[1]), 3, (255, 0, 0), -1)

def draw_trajectory(image, trajectory):
    """
    画像に軌跡を描画する関数
    """
    for i in range(1, len(trajectory)):
        cv2.line(image, (trajectory[i-1][0], trajectory[i-1][1]), (trajectory[i][0], trajectory[i][1]), (0, 255, 0), 2)

def main():
    # 画像の読み込み
    image = cv2.imread("/home/toyoshima/0000.png")

    # 初期の点座標
    initial_point = [50, 50]

    # 点の軌跡を保存するリスト
    trajectory = [initial_point]

    # 点の移動
    for i in range(1, 10):
        new_point = [initial_point[0] + i*10, initial_point[1] + i*10]
        trajectory.append(new_point)

    print(trajectory)

    # 画像に点を描画
    for point in trajectory:
        draw_point(image, point)

    # 画像に軌跡を描画
    draw_trajectory(image, trajectory)

    # 画像を表示
    cv2.imshow("Image with Points and Trajectory", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
