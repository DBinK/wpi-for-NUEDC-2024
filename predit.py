from ultralytics import YOLO
import cv2

from loguru import logger

logger.info(f'加载模型...')

# 加载训练后的模型
# model = YOLO('best.pt')
model = YOLO('models/yolov8n.pt')

def capture_image(cam=0):
    # 用cv2调用摄像头拍一张照
    cap = cv2.VideoCapture(cam)
    ret, img = cap.read()

    logger.info(f'Captured image {ret}')

    cv2.imwrite('output/captured_image.jpg', img)
    cap.release()
    
    return img


def predict(img):
    # 使用YOLO模型进行预测
    results = model(img)

    logger.info(f'用时 {results[0].speed}')

    # 可视化结果
    annotated_img = results[0].plot()

    # 提取预测结果
    boxes = results[0].boxes
    max_area = 0
    max_center = None

    for box in boxes:
        # 只考虑 'person' 类别
        if box.cls == 0:  # 假设 'person' 的类别索引是 0
            x1, y1, x2, y2 = box.xyxy[0]  # 获取边界框坐标
            area = (x2 - x1) * (y2 - y1)  # 计算面积

            # 更新最大面积和中心坐标
            if area > max_area:
                max_area = area
                max_center = ((x1 + x2) / 2, (y1 + y2) / 2)  # 计算中心坐标

    if max_center is not None:
        # 将中心坐标转换为整数
        max_center = (int(max_center[0].item()), int(max_center[1].item()))
        cv2.circle(annotated_img, max_center, 5, (0, 0, 255), -1)
        
        logger.info(f'最大面积的 person 中心坐标: {max_center}')
    else:
        logger.info('未检测到 person')

    return annotated_img,max_center



def find_available_cameras(start_index=0, end_index=9):
    """
    返回在指定范围内所有可用摄像头的索引列表。
    @param start_index: 搜索范围的起始索引
    @param end_index: 搜索范围的结束索引
    @return: 找到的摄像头索引列表
    """
    available_cameras = []
    for index in range(start_index, end_index + 1):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
        else:
            continue  # 如果无法打开，则直接跳过，继续下一个索引
    return available_cameras


if __name__ == '__main__':

    logger.info(f'可用摄像头：{find_available_cameras()}')

    logger.info(f'开始预测')

    cap = cv2.VideoCapture(2)

    if cap is not None:
        while True:
            ret, frame = cap.read()
            if ret:

                PD_frame, max_center = predict(frame)

                logger.info(f'坐标：{max_center}')

                cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
                cv2.imshow("frame", PD_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cv2.destroyAllWindows()
    if cap is not None:
        cap.release()

