import cv2
import numpy as np
def find_center(masked_frame, sample_line_pos):
    color = masked_frame[sample_line_pos]
    try:
        # 找到白色的像素点个数，如寻黑色，则改为0
        white_count = np.sum(color == 255)
        # 找到白色的像素点索引，如寻黑色，则改为0
        white_index = np.where(color == 255)
        # 防止white_count=0的报错
        if white_count == 0:
            white_count = 1
        # 找到黑色像素的中心点位置
        # 计算方法应该是边缘检测，计算白色边缘的位置和/2，即是白色的中央位置。
        center = (white_index[0][white_count - 1] + white_index[0][0]) / 2
        # 计算出center与标准中心点的偏移量
        direction = center - 640 / 2
    except:
        direction = -1

    return direction
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