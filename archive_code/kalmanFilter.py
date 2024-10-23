import numpy as np

dt = 0.1  # 計測間隔
u = np.array([[0.], [0.], [0.], [0.]])  # 外部要素
I = np.identity(4)  # 4次元単位行列


def kalman_filter(x, P, measurements):
    F = np.array([[1., 0., dt, 0.], [0., 1., 0., dt], [0., 0., 1., 0.], [0., 0., 0., 1.]])  # 状態遷移行列
    H = np.array([[1., 0., 0, 0], [0., 1., 0., 0.]])  # 観測行列
    R = np.array([[0.1, 0], [0, 0.1]])  # ノイズ

    for measurement in measurements:
        # 予測
        x_pre = np.dot(F, x) + u
        P = np.dot(np.dot(F, P), F.T)

        # 計測更新
        Z = np.array([measurement])
        y = Z.T - np.dot(H, x_pre)
        S = np.dot(np.dot(H, P), H.T) + R
        K = np.dot(np.dot(P, H.T), np.linalg.inv(S))
        x = x_pre + np.dot(K, y)
        P = np.dot((I - np.dot(K, H)), P)

    return x.tolist(), x_pre.tolist(), P.tolist()


# 初期位置と初期速度を代入した「4次元状態」
initial_xy = [8., 14.]
x = np.array([[initial_xy[0]], [initial_xy[1]], [0.], [0.]])
# 共分散行列
P = np.array([[0., 0., 0., 0.], [0., 0., 0., 0.], [0., 0., 100., 0.], [0., 0., 0., 100.]])

# 新しい計測値
new_measurements = [[9., 13.], [10., 12.], [11., 11.]]

# 更新後の位置と速度の予測値
new_x, new_x_pre, new_P = kalman_filter(x, P, new_measurements)

print("更新後の位置と速度の予測値:", new_x, new_x_pre)