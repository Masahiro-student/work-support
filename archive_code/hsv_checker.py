import cv2

# イメージの読み込み
img = cv2.imread("/home/toyoshima/script/capture/color/0000.png")

# HSV変換
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
img_h, img_s, img_v = cv2.split(img_hsv)

# イメージの表示
cv2.imshow('image', img_h)
cv2.waitKey(0)
cv2.imshow('image', img_s)
cv2.waitKey(0)
cv2.imshow('image', img_v)
cv2.waitKey(0)
cv2.destroyAllWindows()