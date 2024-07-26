import cv2
import time
import numpy as np
from flask import Flask, render_template, Response, request
from loguru import logger

class Streamer:
    def __init__(self):
        self.app = Flask(__name__)
        self.default_frame = np.zeros((500, 500, 3), dtype=np.uint8)
        self.current_frame = self.default_frame.copy()
        self.variables = {
            "变量1": "初始值1",
            "变量2": "初始值2",
            "变量3": "初始值3"
        }

        @self.app.route('/')
        def index():
            return render_template('index.html', variables=self.variables)

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/update_variable', methods=['POST'])
        def update_variable():
            var_name = request.form.get('name')
            new_value = request.form.get('value')
            if var_name in self.variables and new_value:
                self.variables[var_name] = new_value  # 更新变量
                logger.info(f"{var_name} 已更新为: {new_value}")
            return '', 204

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
        self.app.run(host='0.0.0.0', debug=False, threaded=True)  
        # 将 debug 设置为 False，并启用 threaded

if __name__ == '__main__':
    streamer = Streamer()
    streamer.run()