import cv2
import numpy as np
import m2 as md
V_THRESHOLD = 40

def load_mask2():
    mask = np.zeros((720,1280))
    for i in range(285, 915):
        for j in range(255, 612):
            mask[j][i] = 1
    return mask

def load_threshold_m():
    return md.load_hs_threshold("marker_threshold_blue")

def detect_marker(color_img, min_th, max_th, mask):
    # 色度と彩度のしきい値設定
    hsv_arr = cv2.cvtColor(color_img, cv2.COLOR_BGR2HSV)
    hue_arr = hsv_arr[:, :, 0]
    print(hue_arr)
    print(hue_arr.shape)
    print(hue_arr[489,708])
    saturation_arr = hsv_arr[:, :, 1]
    print(saturation_arr)
    print(saturation_arr.shape)
    print(saturation_arr[489,708])
    value_arr = hsv_arr[:, :, 2]
    print(value_arr)
    print(value_arr.shape)
    print(value_arr[489,708])
    #print(hue_arr[293][175])

    hue_min, hue_max = min_th[0], max_th[0]
    saturation_min, saturation_max = min_th[1], max_th[1]
    print(hue_min, hue_max)
    h_meet = np.logical_and(hue_min <= hue_arr, hue_arr <= hue_max)
    s_meet = np.logical_and(
        saturation_min <= saturation_arr, saturation_arr <= saturation_max
    )
    # 明度が低いところは除外
    v_meet = np.where(V_THRESHOLD <= value_arr, True, False)
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

def draw_marker(img, marker):
    cv2.drawContours(      #青でマーカーの輪郭を描画
        img,
        marker.contour,
        -1,
        color=(255, 0, 0))

    cv2.circle(            #青でマーカーの重心を描画
        img,
        (int(marker.center[0]), int(marker.center[1])),
        5,
        color=(0, 0, 0),
        thickness=-1
        )
    
    
color_img = cv2.imread("/home/toyoshima/script/0008.png",cv2.IMREAD_COLOR)
mask = load_mask2()
#print(color_img)
#print(mask)


(min_th, max_th) = load_threshold_m()
#print(min_th,max_th)
hue_min, hue_max = min_th[0], max_th[0]
#print(hue_min, hue_max)

contour = detect_marker(color_img, min_th, max_th, mask)
#print(contour)


cv2.drawContours(      #青でマーカーの輪郭を描画
        color_img,
        contour,
        -1,
        color=(255, 0, 0))
cv2.imshow("img", color_img)
cv2.waitKey(0)