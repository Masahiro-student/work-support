import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
dt = 1
t = 0
T=[]
X=[]
XP=[0]

# カルマンフィルタのパラメータ
# 状態遷移行列 (A) と観測行列 (H) の定義
A = np.array([[1, dt], [0, 1]])  # 2x2の行列
H = np.array([[1, 0]])  # 1x2の行列

# プロセスノイズと観測ノイズの共分散行列の定義
Q = np.array([[0.01, 0.0], [0.0, 0.01]])  # プロセスノイズの共分散行列
R = np.array([[0.1]])  # 観測ノイズの共分散行列

# 状態ベクトルの初期値と共分散行列の初期値
x = np.array([[0], [0]])  # 状態ベクトルの初期値 (位置と速度)
P = np.eye(2)  # 共分散行列の初期値

# 観測データ
observed_data = [1, 2, 3, 4,5,6,7,8,9,10,10,10,9,8,7,6,5,4,4,4,5,7,8,9,10,13,15,14,13,12,10]

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

    #一手先予測
    x_pre = np.dot(A, x)
    XP.append(x_pre[0,0])
   
    print("推定値:", x)
    X.append(x[0,0])
    t = t + dt 
    T.append(t)

XP = np.delete(XP, -1)


print(X)
print(observed_data)
print(XP)
plt.plot(T,X, 'o', color='orange', linewidth=1.0, label='Estimation')
plt.plot(T,observed_data, '*',color='green',label='Obvervation')
plt.plot(T,XP, '*',color='blue',label='Prediction')
# plt.errorbar(T,XT, yerr=XTERR, capsize=5, fmt='o', color='red', ecolor='orange',label='Estimate')
plt.xlabel('T')
plt.ylabel('X')
plt.grid(True)
plt.legend()
plt.show()
plt.savefig('figure01.jpg')
