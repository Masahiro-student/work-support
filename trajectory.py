import numpy as np
import matplotlib.pyplot as plt
import csv


class Trajectory:
    dimension = None
    reach_indices = None
    trajectory = None  #ポイントと時間の組のリスト
    goals = None

    colors=["b","g","r","c","m","y","k"]  #軌跡のプロットに使う色のリスト

    def __init__(self, width, height):  #ここにキネクトの横の長さ縦の長さが入る
        self.dimension = (width, height)
        self.reach_indices = []
        self.trajectory = []
        self.goals = []
    

    def push_goal(self, goal, time):  #正解部品の棚に到達した地点とその時間をgoalに追加
        self.goals.append((goal[0], goal[1], time))
        self.reach_indices.append(len(self.trajectory))

    # 手の軌跡を保管
    def push_point(self, point, time):
        self.trajectory.append((point[0], point[1], time))

    def plot(self):
        first = 0
        for i in range(len(self.reach_indices)):
            last = self.reach_indices[i]
            color = self.colors[i % len(self.colors)]
            self.scatter_data(self.trajectory[first:last], color)
            # self.scatter_data([self.goals[i]], color, "o")
            first = last

        data = [self.trajectory[0]] + self.goals  #軌跡のスタート地点とゴール地点？
        gs, _ = zip(*data) #dataは地点と時間の組のリストなので地点のみを取り出す
        x, y = zip(*gs)  #gsは座標のリストなのでx座標とy座標に分ける
        plt.plot(x, y, color="black", lw=1, linestyle="dashed")
        plt.show()
        f = open('traj.csv', 'w', encoding='utf-8', newline='')  #'w'なので上書き
        writer = csv.writer(f)
        writer.writerow(data)  #dataを書き込む
        f.close()

    def write_trajectory_to_file(self, filename):
        with open(filename, 'a', newline='') as f:  # 'a' は追記モード
            writer = csv.writer(f)
            # 軌跡データをファイルに書き込む
            for point in self.trajectory:
                writer.writerow(point)
    

    def write_goaltime_to_file(self, filename):
        with open(filename, 'a', newline='') as f:  # 'a' は追記モード
            writer = csv.writer(f)
            #ゴール到達タイムをファイルに書き込む
            for goaltime in self.goals:
                writer.writerow(goaltime)



    def scatter_data(self, data, c, m="."):
        if len(data) > 0:
            p, _ = zip(*data)
            u, v = zip(*p)
            plt.scatter(u, v, color=c, marker=m)  #散布図にプロット