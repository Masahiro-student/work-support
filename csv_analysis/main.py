# main.py

import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import plot_module as plt
import read_trajectory as rt
import calculate_module as cal

def list_csv_files(directory):
    """
    指定されたディレクトリ内のCSVファイルをリスト化する関数
    :param directory: CSVファイルを探すディレクトリ
    :return: CSVファイル名のリスト
    """
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

def file_search(csv_files):
     # 利用可能なCSVファイルのリストを表示
    print("Available CSV files:")
    for i, file in enumerate(csv_files):
        print(f"{i}: {file}")

    # ファイルの選択をユーザーに促す
    try:
        file_index = int(input(f"Select a file (0-{len(csv_files)-1}): "))
        if file_index < 0 or file_index >= len(csv_files):
            print("Invalid file index selected.")
            return 
        else :
            return file_index
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    


def main():
    # CSVファイルのパス
    data_dir = 'data'
    
    csv_files = list_csv_files(data_dir)
    if not csv_files:
        print(f"No CSV files found in directory: {data_dir}")
        return
    
    save_figure_dir = 'figures'
    save_trajectory_dir= os.path.join(save_figure_dir, 'trajectory')
    save_speed_dir = os.path.join(save_figure_dir, 'speed')
    save_acceleration_dir = os.path.join(save_figure_dir, 'acceleration')
    
    os.makedirs(save_figure_dir, exist_ok=True)
    os.makedirs(save_trajectory_dir, exist_ok=True)
    os.makedirs(save_speed_dir, exist_ok=True)
    os.makedirs(save_acceleration_dir, exist_ok=True)
    
    
    file_index = file_search(csv_files)
    
    
    file_path = os.path.join(data_dir, csv_files[file_index])
    
    # 'trajectory_' と '.csv' を取り除いて数字の部分だけ抽出
    experiment_date = csv_files[file_index].replace('trajectory_', '').replace('.csv', '')

    save_trajectory_path = os.path.join(save_trajectory_dir, 'trajectory_' + experiment_date)
    save_speed_path = os.path.join(save_speed_dir, 'speed_' + experiment_date)
    save_acceleration_path = os.path.join(save_acceleration_dir, 'acceleration_' + experiment_date)
    
    # CSVファイルを読み込んで座標と時刻を取得
    x, y, t = rt.read_trajectory_data(file_path)

    # 座標データを基に動きをプロット
    plt.plot_trajectory(x, y, save_trajectory_path)
    
    speed = cal.calculate_speed(x, y, t)
    acceleration = cal.calculate_acceleration(speed, t)
    
    plt.plot_speed(t, speed, save_speed_path)
    plt.plot_acceleration(t, acceleration, save_acceleration_path)

if __name__ == "__main__":
    main()
