import time
from machine import SoftI2C, Pin, PWM

class Motor:
    def __init__(self, L_G, L_B, R_G, R_B, BASE_SPEED=0):
        self.L_GO   = PWM(Pin(L_G), freq=100)
        self.L_BACK = PWM(Pin(L_B), freq=100)
        self.R_GO   = PWM(Pin(R_G), freq=100)
        self.R_BACK = PWM(Pin(R_B), freq=100)
        self.BASE_SPEED = BASE_SPEED

    def l_motor(self, speed):
        
        if speed > 0:
            speed = speed + self.BASE_SPEED
            speed = int(max(-1023, min(speed, 1023)))
            self.L_GO.duty(speed)
            self.L_BACK.duty(0)

        elif speed < 0:
            speed = speed - self.BASE_SPEED
            speed = int(max(-1023, min(speed, 1023)))
            self.L_GO.duty(0)
            self.L_BACK.duty(-speed)

        else:
            self.L_GO.duty(0)

    def r_motor(self, speed):
        
        if speed > 0:
            speed = speed + self.BASE_SPEED
            speed = int(max(-1023, min(speed, 1023)))
            self.R_GO.duty(speed)
            self.R_BACK.duty(0)

        elif speed < 0:
            speed = speed - self.BASE_SPEED
            speed = int(max(-1023, min(speed, 1023)))
            self.R_GO.duty(0)
            self.R_BACK.duty(-speed)
            
        else:
            self.R_GO.duty(0)

    def motor(self, v_l, v_r):
        self.l_motor(v_l)
        self.r_motor(v_r)

    def motion(self, v, w):  # v: linear speed, w: angular speed
        v_l = v - w
        v_r = v + w
        self.l_motor(v_l)
        self.r_motor(v_r)

    def stop(self):
        self.L_GO.duty(0)
        self.L_BACK.duty(0)
        self.R_GO.duty(0)
        self.R_BACK.duty(0)

    def test():
        motor = Motor(3,4,2,1)
        while True:
            print("r_motor forward")
            motor.r_motor(200)
            time.sleep(2)    
            
            print("l_motor forward")
            motor.l_motor(100)
            time.sleep(2)
            
            print("stop")
            motor.stop()
            time.sleep(1)
            
            print("move")
            motor.move(200, 80) 
            time.sleep(5)

            print("stop")
            motor.stop()
            time.sleep(3)


if __name__ == '__main__':

    from encoder import HallEncoder
    from pid import PID

    encoder_l = HallEncoder(7, 10)
    encoder_r = HallEncoder(6, 5)


    pid_l = PID(0.8, 0.0, 0.0, setpoint=0)
    pid_r = PID(0.8, 0.0, 0.0, setpoint=0)

    motor = Motor(3,4,2,1)

    pid_l.setpoint = 1000
    pid_r.setpoint = 1000

    start = time.time()
    while time.time() - start < 10:

        v_l_now = encoder_l.get_speed()
        v_r_now = encoder_r.get_speed()
        
        v_l_pwm = pid_l.update(v_l_now)
        v_r_pwm = pid_r.update(v_r_now)
        
        print(f"v_l_now: {v_l_now}, v_r_now: {v_r_now}, v_l: {v_l_pwm}, v_r: {v_r_pwm}")
        motor.motor(v_l_pwm, v_r_pwm)

        time.sleep(0.1)

    pid_l.setpoint = 1500
    pid_r.setpoint = 1500

    start = time.time()
    while time.time() - start < 10:

        v_l_now = encoder_l.get_speed()
        v_r_now = encoder_r.get_speed()
        
        v_l_pwm = pid_l.update(v_l_now)
        v_r_pwm = pid_r.update(v_r_now)
        
        print(f"v_l_now: {v_l_now}, v_r_now: {v_r_now}, v_l: {v_l_pwm}, v_r: {v_r_pwm}")
        motor.motor(v_l_pwm, v_r_pwm)

        time.sleep(0.1)

    motor.stop()
    