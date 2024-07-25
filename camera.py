import cv2
import subprocess
from loguru import logger

class Camera:
    def __init__(self, exposure_time=None, contrast=None):
        """
        初始化摄像头对象。
        @param exposure_time: 曝光时间，单位为us，默认为None
        @param contrast: 对比度，取值范围0~100，默认为None
        """
        self.exposure_time = exposure_time  # 50~10000 us
        self.contrast      = contrast # 0~100

        self.cap = None  # 明确初始化为None

        if self.exposure_time is not None:
            subprocess.run(["v4l2-ctl", "-c", "auto_exposure=1"])
            subprocess.run(["v4l2-ctl", "-c", f"exposure_time_absolute={exposure_time}"])

        if self.contrast is not None:
            subprocess.run(["v4l2-ctl", "-c", f"contrast={contrast}"])

    def find_available_cameras(self, start_index=0, end_index=9):
        available_cameras = []
        for index in range(start_index, end_index + 1):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                available_cameras.append(index)
                cap.release()
        logger.info(f"Cams {available_cameras} are available.")
        return available_cameras

    def VideoCapture(self, index=None):
        if not index:
            camera_index = self.find_available_cameras()
            if camera_index:
                cap = cv2.VideoCapture(camera_index[0])
                if not cap.isOpened():
                    raise ValueError(f"Unable to open camera {camera_index}")
                self.cap = cap  

                # 打印摄像头信息
                result = subprocess.run(["v4l2-ctl", "--device=/dev/video0", "--all"], capture_output=True, text=True)
                logger.info(result.stdout)
                logger.info(f"Camera {camera_index} is initialized.")

                return self.cap
            
            else:
                raise ValueError("No cameras found")
        else:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                raise ValueError(f"Unable to open camera {index}")
            self.cap = cap  
            result = subprocess.run(["v4l2-ctl", "--device=/dev/video0", "--all"], capture_output=True, text=True)
            logger.info(result.stdout)
            logger.info(f"Camera {index} is initialized.")

            return cap
    
    def set_exposure_time(self, exposure_time):
        """
        设置曝光时间。
        @param exposure_time: 曝光时间，单位为us
        """
        self.exposure_time = exposure_time
        subprocess.run(["v4l2-ctl", "-c", "auto_exposure=1"])
        subprocess.run(["v4l2-ctl", "-c", f"exposure_time_absolute={exposure_time}"])

    def set_contrast(self, contrast):
        """
        设置对比度。
        @param contrast: 对比度，取值范围0~100
        """
        self.contrast = contrast
        subprocess.run(["v4l2-ctl", "-c", f"contrast={contrast}"])

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
    cap = cam.VideoCapture()  # 测试摄像头

    if cap is not None:
        while True:
            ret, frame = cap.read()
            if ret:
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()
