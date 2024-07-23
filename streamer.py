import cv2
import time
import numpy as np
from flask import Flask, render_template, Response
from loguru import logger

class Streamer:
    def __init__(self):
        self.app = Flask(__name__)
        self.default_frame = np.zeros((500, 500, 3), dtype=np.uint8)  # 默认的黑色图片
        self.current_frame = self.default_frame.copy()

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def generate_frames(self):
        """
        生成发送Flask服务器的视频帧
        """
        while True:
            if self.current_frame is not None:
                try:
                    _, jpeg_buffer = cv2.imencode('.jpg', self.current_frame)
                    frame_data = jpeg_buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                except Exception as e:
                    logger.error(f"Error processing frame: {e}")
            time.sleep(0.01)  # 防止CPU占用过高

    def update(self, img):
        """
        更新当前显示的图像帧
        """
        self.current_frame = img

    def run(self):
        """
        启动Flask服务器
        """
        self.app.run(host='0.0.0.0', debug=True)

# 如果这个文件被直接运行，则启动服务器
if __name__ == '__main__':
    streamer = Streamer()
    streamer.run()