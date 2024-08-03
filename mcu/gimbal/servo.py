from machine import PWM, Pin  # type: ignore
import time


class Servo:
    def __init__(
        self,
        pin,
        freq      = 50,         # 频率
        min_us    = 500,        # 最小脉宽
        max_us    = 2500,       # 最大脉宽         
        max_angle = 180,        # 舵机可达最大角度
        min_accu  = 0.3,        # 最小精度

        targe_angle     = 90,   # 初始化目标角度
        limit_min_angle = 0,    # 最小角度限制
        limit_max_angle = 180   # 最大角度限制
    ):
        self.pin = pin
        self.pwm = PWM(Pin(pin), freq=freq, duty=0)

        self.freq      = freq      # 频率
        self.min_us    = min_us    # 最小脉宽
        self.max_us    = max_us    # 最大脉宽
        self.max_angle = max_angle # 最大角度
        self.min_accu  = min_accu  # 最小精度

        self.limit_max_angle = limit_max_angle  # 最大角度限制
        self.limit_min_angle = limit_min_angle  # 最小角度限制

        self.targe_angle = targe_angle  # 初始化目标角度
        self.set_angle(targe_angle)

    def set_limit(self, limit_min_angle, limit_max_angle):  # 限制角度
        self.limit_max_angle = limit_max_angle
        self.limit_min_angle = limit_min_angle

    def set_angle(self, targe_angle):  # 绝对角度运动

        print(f"set_angle(): 传入舵机 {self.pin} 目标角度: {targe_angle}")

        targe_angle = min(max(targe_angle, self.limit_min_angle), self.limit_max_angle) # 限制角度

        print(f"set_angle(): 实际舵机 {self.pin} 可达角度: {targe_angle}\n")

        self.targe_angle = targe_angle

        us = self.min_us + (self.max_us - self.min_us) * (targe_angle / self.max_angle)
        ns = int(us * 1000)

        self.pwm.duty_ns(ns)

    def set_angle_relative(self, relative_angle):  # 相对角度运动
        print(f"set_angle_relative(): 传入舵机 {self.pin} 相对角度: {relative_angle}\n")
        self.targe_angle += relative_angle
        self.set_angle(self.targe_angle)

    def step(self, step=1):  # 以最小精度步进N步
        self.set_angle_relative(self.min_accu * step)
        
    def reset(self):  # 复位
        self.set_angle(90)

    def deinit(self):  # 注销舵机
        self.pwm.deinit()

    def test_45(self):
        print("\n45 度角转动测试\n")
        self.set_angle(0)
        time.sleep(1)
        self.set_angle(45)
        time.sleep(1)
        self.set_angle(90)
        time.sleep(1)
        self.set_angle(135)
        time.sleep(1)
        self.set_angle(180)
        time.sleep(1)

    def test_0_180(self):
        print("\n0-180 度角转动测试\n")
        for i in range(0, 180, 1):
            self.set_angle(i)
            time.sleep(0.01)

        for i in range(180, 0, -1):
            self.set_angle(i)
            time.sleep(0.01)

    def test_relative(self):
        print("\n相对角度转动测试\n")
        self.set_angle_relative(90)
        time.sleep(1)
        self.set_angle_relative(-45)
        time.sleep(1)
        self.set_angle_relative(-900)
        time.sleep(1)

    def test_step(self):
        print("\n步进转动测试\n")
        for i in range(0, 30):
            self.step(1)
            time.sleep(0.1)

    def test_scan(self):

        points = []

        def fun(KEY):
            points.append(int(self.targe_angle))
            print(f"在 self.targe_angle 检测到 {points}")

        KEY = Pin(6, Pin.IN, Pin.PULL_UP)  # 构建KEY对象
        KEY.irq(fun, Pin.IRQ_FALLING or Pin.IRQ_RISING)  # 定义中断，下降沿触发

        cnt = 0
        while cnt < 50:
            self.step(-3)
            time.sleep(0.01)
            # print(self.targe_angle)
            cnt += 1

        while True:

            cnt = 0
            while cnt < 100:
                self.step(3)
                time.sleep(0.01)
                # print(self.targe_angle)
                cnt += 1

                print(points)

            cnt = 0
            while cnt < 100:
                self.step(-3)
                time.sleep(0.01)
                # print(self.targe_angle)
                cnt += 1

                print(points)


if __name__ == "__main__":

    # servo_x = Servo(47)
    # servo_x.test_relative()
    # servo_x.test_step()

    servo_y = Servo(5)
    # servo_y.test_relative()
    # servo_y.test_step()

    time.sleep(1)

    servo_y.test_scan()

    time.sleep(1)

    servo_y.set_angle(90)
