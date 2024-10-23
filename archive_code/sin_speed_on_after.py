import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
#input
file_path_kondo_0 = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_171101_7.npy'
file_path_kondo_1 = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_171210_8.npy'
file_path_kondo_2 = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_171306_9.npy'

#out_put
#output_path_kondo_0_0 = '/home/toyoshima/script/hand_detection/cos_take_out/koondo_on_0_0.npy'

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
y_t_0 = kondo_on_0[:, f]
y_t_1 = kondo_on_1[:, f]
y_t_2 = kondo_on_2[:, f]


range_0_0 = np.logical_and(9.85 <= y_t_0[:, 1], y_t_0[:, 1] <= 11.42)
range_0_1 = np.logical_and(11.41 <= y_t_0[:, 1], y_t_0[:, 1] <= 12.93)
range_0_2 = np.logical_and(12.92 <= y_t_0[:, 1], y_t_0[:, 1] <= 14.55)
range_0_3 = np.logical_and(47.3 <= y_t_0[:, 1], y_t_0[:, 1] <= 49.75)

range_1_0 = np.logical_and(5.49 <= y_t_1[:, 1], y_t_1[:, 1] <= 7.27)
range_1_1 = np.logical_and(7.26 <= y_t_1[:, 1], y_t_1[:, 1] <= 8.8)
range_1_2 = np.logical_and(8.79 <= y_t_1[:, 1], y_t_1[:, 1] <= 10.47)
range_1_3 = np.logical_and(10.57 <= y_t_1[:, 1], y_t_1[:, 1] <= 12.38)

range_2_0 = np.logical_and(6.96  <= y_t_2[:, 1], y_t_2[:, 1] <= 8.56)
range_2_1 = np.logical_and(8.55  <= y_t_2[:, 1], y_t_2[:, 1] <= 10.1)
range_2_2 = np.logical_and(10.09 <= y_t_2[:, 1], y_t_2[:, 1] <= 11.72)
range_2_3 = np.logical_and(12.02 <= y_t_2[:, 1], y_t_2[:, 1] <= 13.67)

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






#np.save(output_path_kondo_0_0, sin_0_0)

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
canvas.set_window_title('kondo_on_speed555')
plt.xlabel('時間', fontsize=21)
plt.ylabel('手のy方向の速度', fontsize=21)
plt.ylim(-8,8)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(True)
plt.tight_layout()
plt.show()