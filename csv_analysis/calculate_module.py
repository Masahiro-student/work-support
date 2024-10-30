import numpy as np

def calculate_speed(x, y, t):
    """
    各時刻における速度を計算する関数
    :param x: x座標のリスト
    :param y: y座標のリスト
    :param t: 時刻のリスト
    :return: 各時刻に対応する速度のリスト
    """
    # 座標変化量 (dx, dy) を計算
    dx = np.diff(x)
    dy = np.diff(y)
    
    # 時間変化量 (dt) を計算
    dt = np.diff(t)
    
    # 速度 v を計算
    speed = np.sqrt(dx**2 + dy**2) / dt
    return speed

def calculate_acceleration(speed, t):
    """
    各時刻における加速度を計算する関数
    :param speed: 各時刻における速度のリスト
    :param t: 時刻のリスト
    :return: 各時刻に対応する加速度のリスト
    """
    dv = np.diff(speed)  # 速度の変化量
    dt = np.diff(t[1:])  # 時刻の変化量 (速度はt[1:]に対応)
    
    acceleration = dv / dt
    return acceleration