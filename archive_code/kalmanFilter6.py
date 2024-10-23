import numpy as np
matrix1 = 0.01 * np.eye(2)
matrix2 = 0.01 * np.eye(2)
# カルマンフィルタのパラメータ
# 状態遷移行列 (A) と観測行列 (H) の定義
A = np.array([[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]])  # 4x4の行列
H = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])  # 2x4の行列

# プロセスノイズと観測ノイズの共分散行列の定義
Q = np.block([[matrix1, np.zeros((2, 2))],
                   [np.zeros((2, 2)), matrix2]])
 # プロセスノイズの共分散行列
R = np.array([[0.1, 0.0], [0.0, 0.1]])  # 観測ノイズの共分散行列

# 状態ベクトルの初期値と共分散行列の初期値
x = np.array([[0], [0], [0], [0]])  # 状態ベクトルの初期値 (x位置, x速度, y位置, y速度)
P = np.eye(4)  # 共分散行列の初期値

# 観測データ (2次元)
observed_data = np.array([[1.2, 2.4], [3.6, 4.8], [6.0, 7.2]])

# カルマンフィルタの更新ステップ
for z in observed_data:
    # 予測ステップ
    x = np.dot(A, x)
    P = np.dot(np.dot(A, P), A.T) + Q

    # カルマンゲインの計算
    K = np.dot(np.dot(P, H.T), np.linalg.inv(np.dot(np.dot(H, P), H.T) + R))

    # 更新ステップ
    x = x + np.dot(K, z - np.dot(H, x))
    P = P - np.dot(np.dot(K, H), P)

    print("推定位置:", x[0, 0], x[2, 0])