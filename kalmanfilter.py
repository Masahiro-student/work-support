import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
#xは[w方向の位置，w方向の速度，w方向の加速度，h方向の位置，h方向の速度，h方向の加速度]
#measurementは観測した座標(w,h)

def kalman_filter(x, P, measurement):
    dt = 0.1

    A = np.array([[1, 1*dt, 0.5*dt*dt, 0, 0, 0],
              [0, 1, 1*dt, 0, 0, 0],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 1*dt, 0.5*dt*dt],
              [0, 0, 0, 0, 1, 1*dt],
              [0, 0, 0, 0, 0, 1]])
    
    H = np.array([[1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 1, 0, 0]])
    
    Q = np.eye(6) * 0.03

    #観測誤差
    R = np.array([[0.09, 0],
              [0, 0.07]])
    
        # 予測ステップ
    x_hat = np.dot(A, x)
    P_hat = np.dot(np.dot(A, P), A.T) + Q

    # カルマンゲインの計算
    K = np.dot(np.dot(P_hat, H.T), np.linalg.inv(np.dot(np.dot(H, P_hat), H.T) + R))

    # 観測更新ステップ
    z = measurement
    x = x_hat + np.dot(K, z - np.dot(H, x_hat))
    P = P_hat - np.dot(np.dot(K, H), P_hat)   

    #3期先予測ステップ  何秒後を予測するかをprexdt,preydtで指定　　値が違うのは同じ時より予測精度がいい気がしたから
    prexdt = 0.38
    preydt = 0.35
    A3 = np.array([[1, 1*prexdt, 0.5*prexdt*prexdt, 0, 0, 0],
              [0, 1, 1*prexdt, 0, 0, 0],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 1*preydt, 0.5*preydt*preydt],
              [0, 0, 0, 0, 1, 1*preydt],
              [0, 0, 0, 0, 0, 1]])
    h_pre3 = np.dot(A3,x)

    return x, P, h_pre3


# ダミーの観測データ
measurements = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [6, 8],[6,9],[5,10],[4,11],[3,12],[2,13], [1, 14],[0,15],[-1,16],[-2,17],[-1,18],[1,19],[3,20],[5,21],[7,22],[9,23],[11,24],[13,25]])

