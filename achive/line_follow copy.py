#!/usr/bin/env python3

# 识别的是中线为白色

import cv2
import numpy as np
import camera

# center定义
center = 320
# 打开摄像头，图像尺寸640*480（长*高），opencv存储值为480*640（行*列）
cap = camera.lanuch_camera()

while (1):
    ret, frame = cap.read()
    cv2.imshow("recognize_face", frame)
    # 转化为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray", gray)
    # 大津法二值化
    retval, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    cv2.imshow("dst", dst)
    # 膨胀，白区域变大
    dst = cv2.dilate(dst, None, iterations=2)
    cv2.imshow("dst2", dst)
    # # 腐蚀，白区域变小 #
    dst = cv2.erode(dst, None, iterations=6)
    cv2.imshow("dst3", dst)
    # 单看第400行的像素值v
    color = dst[400]
    

    try:
        # 找到白色的像素点个数，如寻黑色，则改为0
        white_count = np.sum(color == 0)
        # 找到白色的像素点索引，如寻黑色，则改为0
        white_index = np.where(color == 0)
        # 防止white_count=0的报错
        if white_count == 0:
            white_count = 1
        # 找到黑色像素的中心点位置
        # 计算方法应该是边缘检测，计算白色边缘的位置和/2，即是白色的中央位置。
        center = (white_index[0][white_count - 1] + white_index[0][0]) / 2
        # 计算出center与标准中心点的偏移量，因为图像大小是640，因此标准中心是320，因此320不能改。
        direction = center - 320
        print(direction)    
    except:
        continue

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release() #释放cap
cv2.destroyAllWindows()#销毁所有窗口
