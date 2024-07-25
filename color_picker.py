import cv2
import numpy as np

# 鼠标回调函数
def get_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # 获取当前帧的颜色值
        b, g, r = frame[y, x]
        rgb = (r, g, b)
        hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
        print(f"RGB: {rgb}, HSV: {hsv}")

# 打开摄像头
cap = cv2.VideoCapture(0)

cv2.namedWindow("Camera")
cv2.setMouseCallback("Camera", get_color)

while True:
    # 读取摄像头画面
    ret, frame = cap.read()
    if not ret:
        break

    # 显示画面
    cv2.imshow("Camera", frame)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头和关闭窗口
cap.release()
cv2.destroyAllWindows()