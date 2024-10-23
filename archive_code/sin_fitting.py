import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def fit_func(x, a, b, c, d):
    return a * np.cos(b*(x/360.0*np.pi*2 - c)) + d

full_path = '/home/toyoshima/script/hand_detection/cos_take_out/koondo_on_0_0.npy'
# 与えられたデータ
data = np.load(full_path)

# 時間tとy座標を取得
t = data[:, 1]
y = data[:, 0]
dt = np.amax(t) - np.amin(t)
A = np.amax(y) - np.amin(y)
offset = (np.amax(y) + np.amin(y))/2
# パラメータの初期値を設定
initial_guess = (A, 1/dt, 0, offset)

# フィッティング実行
params, covariance = curve_fit(fit_func, t, y, p0=initial_guess, maxfev=2000)

# フィッティング結果を出力
print("Fitted Parameters:")
print("Amplitude:", params[0])
print("Frequency:", params[1])
print("Phase:", params[2])
print("Offset:", params[3])

# フィッティングされたcos波をプロット
plt.scatter(t, y, label='Data')  # 散布図
t_fit = np.linspace(t.min(), t.max(), 100)
y_fit = fit_func(t_fit, *params)
plt.plot(t_fit, y_fit, label='Fitted Cosine', linestyle='--', color='red')
plt.xlabel('Time (t)')
plt.ylabel('y-coordinate')
plt.legend()
plt.show()
