import numpy as np
import cv2
import os

class Marker:
    def __init__(self, min_th, max_th, mask):
        self.V_THRESHOLD = 40     #hsvのvの下限値
        self.min_th = min_th
        self.max_th = max_th
        self.mask = mask

    def compute_center(self):
        if len(self.contour) == 0:
            return np.array([0, 0])
        concatenated_contour = np.concatenate(np.concatenate(self.contour))
        return np.mean((concatenated_contour), axis=0)

    def distance(self, goal):   #不使用
        dx = self.center[0] - goal.u
        dy = self.center[1] - goal.v
        distance = dx*dx + dy*dy
        return np.sqrt(distance)

    def update(self, color_arr):
        contour = self.detect_marker(
            color_arr,
            self.min_th,
            self.max_th,
            self.mask,
        )
        self.contour = contour   #上から二番の２つの輪郭をサイズ2のリストで保持

        self.center = self.compute_center()

    def direction(self):   #不使用
        np_hand = np.array(self.contour)
        c = np.squeeze(np_hand)
        x = c[:,1]
        y = c[:,0]

        def reg1dim(x, y):
            n = len(x)
            a = ((np.dot(x, y)- y.sum() * x.sum()/n)/
               ((x ** 2).sum() - x.sum()**2 / n))
            b = (y.sum() - a * x.sum())/n
            return a, b

        a, b = reg1dim(x, y)
        return a, b

    def detect_marker(self, color_img, min_th, max_th, mask):
        # 色度と彩度のしきい値設定
        hsv_arr = cv2.cvtColor(color_img, cv2.COLOR_BGR2HSV)
        hue_arr = hsv_arr[:, :, 0]
        saturation_arr = hsv_arr[:, :, 1]
        value_arr = hsv_arr[:, :, 2]
        hue_min, hue_max = min_th[0], max_th[0]
        saturation_min, saturation_max = min_th[1], max_th[1]
        h_meet = np.logical_and(hue_min <= hue_arr, hue_arr <= hue_max)
        s_meet = np.logical_and(
            saturation_min <= saturation_arr, saturation_arr <= saturation_max
        )
        # 明度が低いところは除外
        v_meet = np.where(self.V_THRESHOLD <= value_arr, True, False)
        is_hand_area = np.logical_and(np.logical_and(h_meet, s_meet), v_meet)
        # is_hand_area = np.logical_and(h_meet, s_meet)
        # 手領域か否かの条件を適用
        threshed_binarized_arr = is_hand_area
        # maskを適用
        masked_binarized_arr = np.where(mask == 1, threshed_binarized_arr, 0)
        binarized_arr_uint8 = masked_binarized_arr.astype(np.uint8) * 255

        contours, _ = cv2.findContours(binarized_arr_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sorted_contours = sorted(
                contours,
                key=lambda x: len(x),
                reverse=True
                )
        return sorted_contours[0:1]
        # 最も輪郭を構成する点の数が多いものを手の輪郭としている

    def extract_and_fill_contour(self, binarized_arr, contour_num=1, area_threshold=500):    #不使用
        binarized_arr_uint8 = binarized_arr.astype(np.uint8) * 255
        contours, _ = cv2.findContours(
            binarized_arr_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        contours_arr = np.array(contours)
        # max_contour = max(contours, key=lambda x: cv2.contourArea(x))
        # しきい値を満たす輪郭を大きい順に最大contour_num個採用
        contour_areas = np.array([cv2.contourArea(contour) for contour in contours_arr])
        sorted_contour_area_indices = np.argsort(contour_areas)[::-1]
        contour_candidates_num = min(len(contours_arr), contour_num)
        contour_candidates = contours_arr[
            [sorted_contour_area_indices[i] for i in range(contour_candidates_num)]
        ]
        extracted_contours = []
        segmented_arr_list = []
        approximated_segmented_arr_list = []
        # 正確な輪郭と近似した輪郭それぞれで塗りつぶした結果を取得（輪郭は近似した結果のみ取得）
        for candidate in contour_candidates:
            if cv2.contourArea(candidate) < area_threshold:
                break
            # 輪郭を描画・保存
            segmented_arr = np.zeros_like(binarized_arr_uint8, dtype=np.uint8)
            cv2.fillPoly(segmented_arr, [candidate], 1).astype(np.bool)
            segmented_arr_list.append(segmented_arr)
            # 近似輪郭を描画・保存
            approximated_segmented_arr = np.zeros_like(binarized_arr_uint8, dtype=np.uint8)
            approximated_candidate = cv2.approxPolyDP(
                candidate, cv2.arcLength(candidate, True) * 0.003, True
            )
            cv2.fillPoly(approximated_segmented_arr, [approximated_candidate], 1).astype(
                np.bool
            )
            approximated_segmented_arr_list.append(approximated_segmented_arr)
            # 輪郭のポリゴンを保存
            extracted_contours.append(approximated_candidate)
        return segmented_arr_list, approximated_segmented_arr_list, extracted_contours

    def load_hs_threshold(threshold_file="background_threshold"):
        threshold_arr = np.loadtxt(f"{os.path.dirname(__file__)}/threshold_file/{threshold_file}.txt")
        if threshold_arr.shape != (2, 2):
            raise Exception(f"threshold file has invalid data shape {threshold_arr.shape}")
        min_threshold = tuple(threshold_arr[0])
        max_threshold = tuple(threshold_arr[1])
        return min_threshold, max_threshold
