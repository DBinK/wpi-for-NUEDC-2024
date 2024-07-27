from machine import PWM, Pin  # type: ignore
import math
import time

class Servo:
    def __init__(
        self, pin, freq=50, min_us=500, max_us=2500, max_angle=180, min_accu=0.3
    ):
        self.pwm = PWM(Pin(pin), freq=freq, duty=0)

        self.freq      = freq      # 频率
        self.min_us    = min_us    # 最小脉宽
        self.max_us    = max_us    # 最大脉宽
        self.max_angle = max_angle # 最大角度
        self.min_accu  = min_accu  # 最小精度

        self.targe_angle = 0       # 目标角度

    def set_angle(self, targe_angle):  #绝对角度运动

        print(f"当前目标角度: {targe_angle}")

        targe_angle = min(max(targe_angle, 0), self.max_angle)

        self.targe_angle = targe_angle

        self.us = self.min_us + (self.max_us - self.min_us) * (targe_angle / self.max_angle)
        ns = int(self.us * 1000)
        self.pwm.duty_ns(ns)

    def set_angle_relative(self, relative_angle):  # 相对角度运动
        print(f"目标相对运动角度: {self.relative_angle}")
        self.targe_angle += relative_angle
        self.set_angle(self.targe_angle)

    def step(self, step=1): # 以最小精度步进N步
        self.set_angle_relative(self.min_accu * step)

    def deinit(self): # 注销舵机
        self.pwm.deinit()

    def test(self):
        
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

        print("\n0-180 度角转动测试\n")
        for i in range(0, 180, 1):
            self.set_angle(i)
            time.sleep(0.01)
            
        for i in range(180, 0, -1):
            self.set_angle(i)
            time.sleep(0.01)
        
        print("\n相对角度转动测试\n")
        self.set_angle_relative(90)
        time.sleep(1)
        self.set_angle_relative(-45)
        time.sleep(1)
        self.set_angle_relative(-90)
        time.sleep(1)
        
        print("\n步进转动测试\n")
        for i in range(0, 30):
            self.step()
            time.sleep(1)
            
        self.deinit()

if __name__ == "__main__":

    servo = Servo(4)
    servo.test()