import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import matplotlib.font_manager as fm
#input

font_path = "/home/toyoshima/.local/lib/python3.6/site-packages/cv2/qt/fonts/DejaVuSans-Bold.ttf"
font_prop = fm.FontProperties(fname=font_path)

file_path_kondo_0 = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_170303_0.npy'
file_path_kondo_1 = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_170445_1.npy'
file_path_kondo_2 = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_170552_2.npy'


#out_put
output_path_kondo_0_0 = '/home/toyoshima/script/hand_detection/cos_take_out/koondo_on_0_0.npy'

# ファイルを読み込む
kondo_on_0 = np.load(file_path_kondo_0)
kondo_on_1 = np.load(file_path_kondo_1)
kondo_on_2 = np.load(file_path_kondo_2)

def normalize(sin_x_x):
    y = sin_x_x[:, 0]
    t = sin_x_x[:, 1]
    sin_x_x[:, 0] -= np.amin(y)
    sin_x_x[:, 1] -= np.amin(t)

    sin_x_x[:, 0] /= np.amax(y)
    sin_x_x[:, 1] /= np.amax(t)
    return sin_x_x

def normalize2(sin_x_x):
    y = sin_x_x[:, 0]
    t = sin_x_x[:, 1]
    y_range = 616 - 170
    sin_x_x[:, 0] = (616 - sin_x_x[:, 0]) / y_range
    sin_x_x[:, 1] -= np.amin(t)

    sin_x_x[:, 1] /= np.amax(t)
    return sin_x_x

def reverse(array):
    array[:, 0] = 1 - array[:, 0]
    return array

#x座標を取り除く
f = [False, True, True]  
y_t_0 = kondo_on_0[:, f]
y_t_1 = kondo_on_1[:, f]
y_t_2 = kondo_on_2[:, f]

range_0_0 = np.logical_and(40.6 <= y_t_0[:, 1], y_t_0[:, 1] <= 42.9)
range_0_1 = np.logical_and(42.9 <= y_t_0[:, 1], y_t_0[:, 1] <= 45.16)
range_0_2 = np.logical_and(45.14 <= y_t_0[:, 1], y_t_0[:, 1] <= 47.34)
range_0_3 = np.logical_and(47.3 <= y_t_0[:, 1], y_t_0[:, 1] <= 49.75)

range_1_0 = np.logical_and(7.14 <= y_t_1[:, 1], y_t_1[:, 1] <= 8.94)
range_1_1 = np.logical_and(8.93 <= y_t_1[:, 1], y_t_1[:, 1] <= 10.73)
range_1_2 = np.logical_and(10.72 <= y_t_1[:, 1], y_t_1[:, 1] <= 12.76)
range_1_3 = np.logical_and(12.74 <= y_t_1[:, 1], y_t_1[:, 1] <= 15.46)

range_2_0 = np.logical_and(6.7  <= y_t_2[:, 1], y_t_2[:, 1] <= 8.54)
range_2_1 = np.logical_and(8.53  <= y_t_2[:, 1], y_t_2[:, 1] <= 10.11)
range_2_2 = np.logical_and(10.21 <= y_t_2[:, 1], y_t_2[:, 1] <= 11.94)
range_2_3 = np.logical_and(12.02 <= y_t_2[:, 1], y_t_2[:, 1] <= 13.67)

sin_0_0 = (normalize2(y_t_0[range_0_0]))
sin_0_1 = (normalize2(y_t_0[range_0_1]))
sin_0_2 = (normalize2(y_t_0[range_0_2]))
sin_0_3 = (normalize2(y_t_0[range_0_3]))

sin_1_0 = (normalize2(y_t_1[range_1_0]))
sin_1_1 = (normalize2(y_t_1[range_1_1]))
sin_1_2 = (normalize2(y_t_1[range_1_2]))
sin_1_3 = (normalize2(y_t_1[range_1_3]))

sin_2_0 = (normalize2(y_t_2[range_2_0]))
sin_2_1 = (normalize2(y_t_2[range_2_1]))
sin_2_2 = (normalize2(y_t_2[range_2_2]))
sin_2_3 = (normalize2(y_t_2[range_2_3]))

np.save(output_path_kondo_0_0, sin_0_0)

plt.plot(sin_0_0[:,1],sin_0_0[:,0], 'o', color='blue', markersize=2)
plt.plot(sin_0_1[:,1],sin_0_1[:,0], 'o', color='red', markersize=2)
plt.plot(sin_0_2[:,1],sin_0_2[:,0], 'o', color='green', markersize=2)
#plt.plot(sin_0_3[:,1],sin_0_3[:,0], 'o', color='m', markersize=2)

plt.plot(sin_1_0[:,1],sin_1_0[:,0], 'o', color='blue', markersize=2)
plt.plot(sin_1_1[:,1],sin_1_1[:,0], 'o', color='red', markersize=2)
plt.plot(sin_1_2[:,1],sin_1_2[:,0], 'o', color='green', markersize=2)
plt.plot(sin_1_3[:,1],sin_1_3[:,0], 'o', color='m', markersize=2)

plt.plot(sin_2_0[:,1],sin_2_0[:,0], 'o', color='blue', markersize=2)
plt.plot(sin_2_1[:,1],sin_2_1[:,0], 'o', color='red', markersize=2)
plt.plot(sin_2_2[:,1],sin_2_2[:,0], 'o', color='green', markersize=2)
#plt.plot(sin_2_3[:,1],sin_2_3[:,0], 'o', color='m', markersize=2)
#plt.plot(T,observation[:, 1], '*',color='green',label='Obvervation')
#plt.plot(T,tp[:,3], '*',color='blue',label='Prediction')
# plt.errorbar(T,XT, yerr=XTERR, capsize=5, fmt='o', color='red', ecolor='orange',label='Estimate')
fig = plt.gcf()
canvas = fig.canvas
canvas.set_window_title('kondo_on_sin_555')
plt.xlabel('時間', fontsize=21)  # 日本語ラベル
plt.ylabel('手のy座標', fontsize=21)
plt.xlim(0,1)
plt.ylim(0,1)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(True)
plt.tight_layout()
plt.show()