import numpy as np
file_path = '/home/toyoshima/script/hand_detection/exp_module/kondo/traj_time/traj_time_20240118_170303_0.npy'

# ファイルを読み込む
loaded_data = np.load(file_path)

# 読み込んだデータを表示
print(loaded_data)