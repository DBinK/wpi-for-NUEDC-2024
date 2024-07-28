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

        logger.info(f"Cams testing.")

        for index in range(start_index, end_index + 1):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                available_cameras.append(index)
                cap.release()
        logger.info(f"Cams {available_cameras} are available.")
        return available_cameras
    
    def get_camera_serial(camera_index):

        command = f'udevadm info --name=/dev/video{camera_index} | grep ID_SERIAL='
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output, _ = p.communicate()
        serial = output.decode().strip().split('=')[1] if output else None

        return serial

    def VideoCapture(self, index=None, camera_name=None):
        
        if not index and not camera_name:
            camera_index = self.find_available_cameras()
            if camera_index:
                cap = cv2.VideoCapture(camera_index[0])
                if not cap.isOpened():
                    raise ValueError(f"Unable to open camera {camera_index}")
                self.cap = cap  
            else:
                raise ValueError("No cameras found")
            
        elif index:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                raise ValueError(f"Unable to open camera {index}")
            self.cap = cap  
            
        elif camera_name:
            camera_index = self.find_camera_id(camera_name)            
            if camera_index:
                cap = cv2.VideoCapture(camera_index)
                if not cap.isOpened():
                    raise ValueError(f"Unable to open camera {camera_index}")
                self.cap = cap  
            else:
                raise ValueError("No cameras found")

        result = subprocess.run(["v4l2-ctl", "--all"], capture_output=True, text=True)
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

    def find_camera_id(self, camera_name): # 从 v4l2-ctl --list-devices 获取 camera_name
        # 运行命令并获取输出
        output = subprocess.check_output(['v4l2-ctl', '--list-devices'], text=True)

        # 初始化字典
        device_dict = {}

        # 处理输出
        lines = output.strip().split('\n')
        device_name = None

        for line in lines:
            line = line.strip()
            if line:  # 如果行不为空
                if line.endswith(':'):
                    # 这是设备名
                    device_name = line[:-1]  # 去掉末尾的冒号
                else:
                    # 这是设备路径
                    device_path = line
                    # 将设备名和设备路径存入字典
                    if device_name in device_dict:
                        device_dict[device_name].append(device_path)
                    else:
                        device_dict[device_name] = [device_path]

        camera_id = int(device_dict[camera_name][0][10])
        logger.info(device_dict)
        logger.info(camera_id)

        return camera_id

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
    cam = Camera()  # 实例化Camera类
    cap = cam.VideoCapture(
        camera_name = 'HD Camera: HD Camera (usb-0000:00:14.0-3.4)'
        )  # 测试摄像头

    if cap is not None:
        while True:
            ret, frame = cap.read()
            if ret:
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()
