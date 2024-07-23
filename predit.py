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

    cv2.imwrite('captured_image.jpg', img)
    cap.release()
    
    return img

def predict(img):
    # 使用YOLO模型进行预测
    results = model(img)

    logger.info(f'用时 {results[0].speed}')

    # 可视化结果
    annotated_img = results[0].plot()
    cv2.imwrite('predicted_image.jpg', annotated_img)

    return annotated_img


if __name__ == '__main__':

    logger.info(f'开始预测')

    img = capture_image(0)

    predict(img)
    

