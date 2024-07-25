import cv2
import subprocess
from loguru import logger

class Camera:
    def __init__(self, exposure_time=None):
        """
        初始化摄像头对象。
        @param exposure_time: 曝光时间，单位为us，默认为None
        """
        self.exposure_time = exposure_time  # 50~10000 us
        self.cap = None  # 明确初始化为None

        if self.exposure_time is not None:
            subprocess.run(["v4l2-ctl", "-c", "auto_exposure=1"])
            subprocess.run(["v4l2-ctl", "-c", f"exposure_time_absolute={exposure_time}"])

        self.init_camera()  # 确保在__init__之后调用

    def find_available_cameras(self, start_index=0, end_index=9):
        available_cameras = []
        for index in range(start_index, end_index + 1):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                available_cameras.append(index)
                cap.release()
        logger.info(f"Cams {available_cameras} are available.")
        return available_cameras

    def init_camera(self):
        camera_index = self.find_available_cameras()
        if camera_index:
            cap = cv2.VideoCapture(camera_index[0])
            if not cap.isOpened():
                raise ValueError(f"Unable to open camera {camera_index}")
            self.cap = cap  

            # 打印摄像头信息
            result = subprocess.run(["v4l2-ctl", "--device=/dev/video0", "--all"], capture_output=True, text=True)
            logger.info(f"Camera {result.stdout} is initialized.")

            return self.cap
        
        else:
            raise ValueError("No cameras found")

    def test(self):
        if self.cap is not None:
            while True:
                ret, frame = self.cap.read()
                if ret:
                    cv2.imshow("frame", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        cv2.destroyAllWindows()
        if self.cap is not None:
            self.cap.release()
            

if __name__ == "__main__":
    cam = Camera(1000)  # 实例化Camera类
    cam.test()  # 测试摄像头