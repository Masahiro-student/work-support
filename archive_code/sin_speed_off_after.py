import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
#input
file_path_kondo_0 = '/home/toyoshima/script/hand_detection/exp_no_support/kondo/traj_time/traj_time_20240118_174145_7.npy'
file_path_kondo_1 = '/home/toyoshima/script/hand_detection/exp_no_support/kondo/traj_time/traj_time_20240118_174247_8.npy'
file_path_kondo_2 = '/home/toyoshima/script/hand_detection/exp_no_support/kondo/traj_time/traj_time_20240118_174347_9.npy'

#out_put
output_path_kondo_0_0 = '/home/toyoshima/script/hand_detection/cos_take_out/koondo_on_0_0.npy'

# ファイルを読み込む
kondo_off_0 = np.load(file_path_kondo_0)
kondo_off_1 = np.load(file_path_kondo_1)
kondo_off_2 = np.load(file_path_kondo_2)

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

def speed(array):
    speed_array = []
    for i in range(array.shape[0] - 1):
        v = (array[i][0] - array[i+1][0]) / (array[i][1] - array[i+1][1])
        t = (array[i][1] + array[i+1][1]) / 2
        speed_array.append([v, t])
    speed_array = np.array(speed_array)
    return speed_array

#x座標を取り除く
f = [False, True, True]  
y_t_0 = kondo_off_0[:, f]
y_t_1 = kondo_off_1[:, f]
y_t_2 = kondo_off_2[:, f]

range_0_0 = np.logical_and(4.28 <= y_t_0[:, 1], y_t_0[:, 1] <= 5.86)
range_0_1 = np.logical_and(5.85 <= y_t_0[:, 1], y_t_0[:, 1] <= 7.14)
range_0_2 = np.logical_and(7.13 <= y_t_0[:, 1], y_t_0[:, 1] <= 8.31)
range_0_3 = np.logical_and(8.3 <= y_t_0[:, 1], y_t_0[:, 1] <= 9.94)

range_1_0 = np.logical_and(4.32 <= y_t_1[:, 1], y_t_1[:, 1] <= 5.92)
range_1_1 = np.logical_and(5.9 <= y_t_1[:, 1], y_t_1[:, 1] <= 7.36)
range_1_2 = np.logical_and(7.57 <= y_t_1[:, 1], y_t_1[:, 1] <= 8.96)
range_1_3 = np.logical_and(9.04 <= y_t_1[:, 1], y_t_1[:, 1] <= 11.02)

range_2_1 = np.logical_and(4.06 <= y_t_2[:, 1], y_t_2[:, 1] <= 5.56)
range_2_2 = np.logical_and(5.55   <= y_t_2[:, 1], y_t_2[:, 1] <= 7.09)
range_2_0 = np.logical_and(7.07 <= y_t_2[:, 1], y_t_2[:, 1] <= 8.48)
range_2_3 = np.logical_and(8.63 <= y_t_2[:, 1], y_t_2[:, 1] <= 10.29)

sin_0_0 = speed(normalize2(y_t_0[range_0_0]))
sin_0_1 = speed(normalize2(y_t_0[range_0_1]))
sin_0_2 = speed(normalize2(y_t_0[range_0_2]))
sin_0_3 = speed(normalize2(y_t_0[range_0_3]))

sin_1_0 = speed(normalize2(y_t_1[range_1_0]))
sin_1_1 = speed(normalize2(y_t_1[range_1_1]))
sin_1_2 = speed(normalize2(y_t_1[range_1_2]))
sin_1_3 = speed(normalize2(y_t_1[range_1_3]))

sin_2_0 = speed(normalize2(y_t_2[range_2_0]))
sin_2_1 = speed(normalize2(y_t_2[range_2_1]))
sin_2_2 = speed(normalize2(y_t_2[range_2_2]))
sin_2_3 = speed(normalize2(y_t_2[range_2_3]))

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
canvas.set_window_title('kondo_off_speed555')
plt.xlabel('時間', fontsize=21)
plt.ylabel('手のy方向の速度', fontsize=21)
plt.ylim(-8,8)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(True)
plt.tight_layout()
plt.show()