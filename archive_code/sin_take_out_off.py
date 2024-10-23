import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
#input
file_path_kondo_0 = '/home/toyoshima/script/hand_detection/exp_no_support/kondo/traj_time/traj_time_20240118_173502_0.npy'
file_path_kondo_1 = '/home/toyoshima/script/hand_detection/exp_no_support/kondo/traj_time/traj_time_20240118_173608_1.npy'
file_path_kondo_2 = '/home/toyoshima/script/hand_detection/exp_no_support/kondo/traj_time/traj_time_20240118_173700_2.npy'

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
    sin_x_x[:, 0] = (sin_x_x[:, 0] - 170) / y_range
    sin_x_x[:, 1] -= np.amin(t)

    sin_x_x[:, 1] /= np.amax(t)
    return sin_x_x

def reverse(array):
    array[:, 0] = 1 - array[:, 0]
    return array

#x座標を取り除く
f = [False, True, True]  
y_t_0 = kondo_off_0[:, f]
y_t_1 = kondo_off_1[:, f]
y_t_2 = kondo_off_2[:, f]

range_0_0 = np.logical_and(14.67 <= y_t_0[:, 1], y_t_0[:, 1] <= 16.4)
range_0_1 = np.logical_and(16.47 <= y_t_0[:, 1], y_t_0[:, 1] <= 18.13)
range_0_2 = np.logical_and(18.1 <= y_t_0[:, 1], y_t_0[:, 1] <= 19.7)
range_0_3 = np.logical_and(19.83 <= y_t_0[:, 1], y_t_0[:, 1] <= 21.7)

range_1_0 = np.logical_and(6.42 <= y_t_1[:, 1], y_t_1[:, 1] <= 7.93)
range_1_1 = np.logical_and(7.92 <= y_t_1[:, 1], y_t_1[:, 1] <= 9.34)
range_1_2 = np.logical_and(9.33 <= y_t_1[:, 1], y_t_1[:, 1] <= 10.74)
range_1_3 = np.logical_and(10.9 <= y_t_1[:, 1], y_t_1[:, 1] <= 12.8)

range_2_1 = np.logical_and(5.59 <= y_t_2[:, 1], y_t_2[:, 1] <= 7.04)
range_2_2 = np.logical_and(7.03   <= y_t_2[:, 1], y_t_2[:, 1] <= 8.41)
range_2_0 = np.logical_and(8.4 <= y_t_2[:, 1], y_t_2[:, 1] <= 9.7)
range_2_3 = np.logical_and(9.78 <= y_t_2[:, 1], y_t_2[:, 1] <= 11.5)

range_3_1 = np.logical_and(5.58 <= y_t_2[:, 1], y_t_2[:, 1] <= 7.01)
range_3_2 = np.logical_and(7    <= y_t_2[:, 1], y_t_2[:, 1] <= 8.36)
range_3_0 = np.logical_and(4.13 <= y_t_2[:, 1], y_t_2[:, 1] <= 5.6)
range_3_3 = np.logical_and(8.45 <= y_t_2[:, 1], y_t_2[:, 1] <= 9.86)

sin_0_0 = reverse(normalize2(y_t_0[range_0_0]))
sin_0_1 = reverse(normalize2(y_t_0[range_0_1]))
sin_0_2 = reverse(normalize2(y_t_0[range_0_2]))
sin_0_3 = reverse(normalize2(y_t_0[range_0_3]))

sin_1_0 = reverse(normalize2(y_t_1[range_1_0]))
sin_1_1 = reverse(normalize2(y_t_1[range_1_1]))
sin_1_2 = reverse(normalize2(y_t_1[range_1_2]))
sin_1_3 = reverse(normalize2(y_t_1[range_1_3]))

sin_2_0 = reverse(normalize2(y_t_2[range_2_0]))
sin_2_1 = reverse(normalize2(y_t_2[range_2_1]))
sin_2_2 = reverse(normalize2(y_t_2[range_2_2]))
sin_2_3 = reverse(normalize2(y_t_2[range_2_3]))

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
canvas.set_window_title('kondo_off_sin_555')
plt.xlabel('時間', fontsize=21)
plt.ylabel('手のy座標', fontsize=21)
plt.xlim(0,1)
plt.ylim(0,1)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(True)
plt.tight_layout()
plt.show()