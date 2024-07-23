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
    cv2.imwrite('output/predicted_image.jpg', annotated_img)

    return annotated_img
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

    img = capture_image(0)

    predict(img)
    

