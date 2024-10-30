import matplotlib.pyplot as plt
import os

def plot_trajectory(x, y, save_path=None):
    """
    座標データから動きをプロットする関数
    :param x: x座標のリスト
    :param y: y座標のリスト
    """
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', color='b', linestyle='-', markersize=5)
    plt.title('Trajectory of Points Over Time')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    
    # 保存する場合はsave_pathを指定
    if save_path:
        check_and_remove_file(save_path)
        plt.savefig(save_path)
        print(f"Trajectory plot saved as: {save_path}")
    
    # グラフを表示
    # plt.show()
    
def plot_speed(t, speed, save_path=None):
    """
    速度をプロットする関数
    :param t: 時刻のリスト
    :param speed: 速度のリスト
    """
    plt.figure(figsize=(8, 6))
    # 時刻 t の中で、速度が計算できるのは 1つ少ないので t[1:] を使う
    plt.plot(t[1:], speed, marker='o', color='r', linestyle='-', markersize=5)
    plt.title('Speed Over Time')
    plt.xlim(0, 30)
    plt.xlabel('Time')
    plt.ylabel('Speed')
    plt.grid(True)
    
    # 保存する場合はsave_pathを指定
    if save_path:
        check_and_remove_file(save_path)
        plt.savefig(save_path)
        print(f"Speed plot saved as: {save_path}")
    
    # plt.show()
    
def plot_acceleration(t, acceleration, save_path=None):
    """
    加速度データをプロットし、保存する関数
    :param t: 時刻のリスト
    :param acceleration: 加速度のリスト
    :param save_path: 画像を保存するパス (指定があれば)
    """
    plt.figure(figsize=(8, 6))
    plt.plot(t[2:], acceleration, marker='o', color='g', linestyle='-', markersize=5)
    plt.title('Acceleration Over Time')
    plt.xlim(0, 30)
    plt.ylim(-5000, 5000)
    plt.xlabel('Time')
    plt.ylabel('Acceleration')
    plt.grid(True)

    # 保存する場合
    if save_path:   
        check_and_remove_file(save_path)
        plt.savefig(save_path)
        print(f"Acceleration plot saved as: {save_path}")
    
    # plt.show()
    
def check_and_remove_file(file_path):
    """
    同名のファイルが存在する場合、そのファイルを削除する関数
    :param file_path: チェックするファイルパス
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Existing file {file_path} has been removed.")
    
