from machine import SoftI2C, Pin, PWM

class RobotController:
    def __init__(self):
        self.KEY = Pin(0, Pin.IN, Pin.PULL_UP)
        self.SPEED_LIMIT = 1023
        self.init_motors()

    def init_motors(self):
        self.LB_back = PWM(Pin(15), freq=50)
        self.LB_go   = PWM(Pin(16), freq=50)
        self.LF_back = PWM(Pin(17), freq=50)
        self.LF_go   = PWM(Pin(18), freq=50)
        self.RB_back = PWM(Pin(21), freq=50)
        self.RB_go   = PWM(Pin(34), freq=50)
        self.RF_back = PWM(Pin(35), freq=50)
        self.RF_go   = PWM(Pin(36), freq=50)

    def set_motor(self, motor_name, pwm_val):
        if pwm_val > 0:
            getattr(self, f"{motor_name}_go").duty(pwm_val)
            getattr(self, f"{motor_name}_back").duty(0)
        elif pwm_val < 0:
            getattr(self, f"{motor_name}_back").duty(-pwm_val)
            getattr(self, f"{motor_name}_go").duty(0)
        elif pwm_val == 0:
            getattr(self, f"{motor_name}_back").duty(0)
            getattr(self, f"{motor_name}_go").duty(0)

    def move_wheel(self, wheel, pwm_val):
        if wheel == "LF":
            self.set_motor("LF", pwm_val)
        elif wheel == "LB":
            self.set_motor("LB", pwm_val)
        elif wheel == "RF":
            self.set_motor("RF", pwm_val)
        elif wheel == "RB":
            self.set_motor("RB", pwm_val)

    def move(self, v_y, v_x, v_w):
        v1, v2, v3, v4 = v_y + v_x - v_w, v_y - v_x - v_w, v_y - v_x + v_w, v_y + v_x + v_w
        v1, v2, v3, v4 = [max(-(self.SPEED_LIMIT), min(self.SPEED_LIMIT, val)) for val in [v1, v2, v3, v4]]
        
        self.move_wheel("LF", v1)
        self.move_wheel("LB", v2)
        self.move_wheel("RF", v3)
        self.move_wheel("RB", v4)

    def go_forward(self, pwm_val):
        self.move(pwm_val, 0, 0)

    def go_backward(self, pwm_val):
        self.move(-pwm_val, 0, 0)

    def go_left(self, pwm_val):
        self.move(0, -pwm_val, 0)

    def go_right(self, pwm_val):
        self.move(0, pwm_val, 0)

    def turn_left(self, pwm_val):
        self.move(0, 0, pwm_val)

    def turn_right(self, pwm_val):
        self.move(0, 0, -pwm_val)

    def stop(self):
        self.move(0, 0, 0)

if __name__ == "__main__":
    # 测试所有功能
    robot = RobotController()
    while True:
        robot.go_forward(50)
        robot.go_backward(50)
        robot.go_left(50)
        robot.go_right(50)
        robot.turn_left(50)
        robot.turn_right(50)
        robot.stop()
    

