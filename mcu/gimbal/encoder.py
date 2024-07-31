from machine import Pin
import time

class HallEncoder:
    def __init__(self, pin_a, pin_b):
        self.pin_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.pin_b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.position = 0
        self.last_a = self.pin_a.value()
        
        # 设置中断
        self.pin_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.update_position)
        self.pin_b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.update_position)

    def update_position(self, pin):
        current_a = self.pin_a.value()
        current_b = self.pin_b.value()
        
        if current_a != self.last_a:  # 只有在A引脚状态变化时才处理
            if current_a == 1:  # A引脚上升沿
                if current_b == 0:  # B引脚为低，顺时针旋转
                    self.position += 1
                else:  # B引脚为高，逆时针旋转
                    self.position -= 1
            self.last_a = current_a

    def get_position(self):
        return self.position

# 示例使用
if __name__ == "__main__":
    encoder = HallEncoder(pin_a=2, pin_b=1)  # 根据实际连接的引脚修改
    try:
        while True:
            print("当前编码器位置:", encoder.get_position())
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("程序结束")