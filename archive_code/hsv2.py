
import cv2
import os

# 対象画像読み込み
img = cv2.imread("/home/toyoshima/script/capture/color/0001.png",cv2.IMREAD_COLOR)

# 対象範囲を切り出し
boxFromX = 460 #対象範囲開始位置 X座標
boxFromY = 560 #対象範囲開始位置 Y座標
boxToX = 478 #対象範囲終了位置 X座標
boxToY = 575 #対象範囲終了位置 Y座標
# y:y+h, x:x+w　の順で設定
imgBox = img[boxFromY: boxToY, boxFromX: boxToX]
#print(imgBox)
# RGB平均値を出力
# flattenで一次元化しmeanで平均を取得 
b = imgBox.T[0].flatten().mean()
g = imgBox.T[1].flatten().mean()
r = imgBox.T[2].flatten().mean()

# RGB平均値を取得
print("B: %.2f" % (b))
print("G: %.2f" % (g))
print("R: %.2f" % (r))

# BGRからHSVに変換
imgBoxHsv = cv2.cvtColor(imgBox,cv2.COLOR_BGR2HSV)

hue_arr = imgBoxHsv[:, :, 0]
saturation_arr = imgBoxHsv[:, :, 1]
value_arr = imgBoxHsv[:, :, 2]

print(hue_arr)

# HSV平均値を取得
# flattenで一次元化しmeanで平均を取得 
h = imgBoxHsv.T[0].flatten().mean()
s = imgBoxHsv.T[1].flatten().mean()
v = imgBoxHsv.T[2].flatten().mean()

# HSV平均値を出力
# uHeは[0,179], Saturationは[0,255]，Valueは[0,255]
print("Hue: %.2f" % (h))
print("Salute: %.2f" % (s))
print("Value: %.2f" % (v))
cv2.imshow('img',imgBox)
cv2.waitKey(0)
