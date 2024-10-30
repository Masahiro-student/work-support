import pandas as pd

def read_trajectory_data(file_path):
    """
    CSVファイルから座標と時刻データを読み込む関数
    :param file_path: 読み込むCSVファイルのパス
    :return: x座標, y座標, 時刻のリスト
    """
    # CSVファイルを読み込む
    df = pd.read_csv(file_path)

    # 各列を変数に格納
    x_coordinates = df.iloc[:, 0]  # 1列目: x座標
    y_coordinates = df.iloc[:, 1]  # 2列目: y座標
    timestamps = df.iloc[:, 2]     # 3列目: 時刻

    return x_coordinates, y_coordinates, timestamps