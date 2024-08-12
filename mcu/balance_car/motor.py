from time import sleep
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

    def stop(self):
        self.L_GO.duty(0)
        self.L_BACK.duty(0)
        self.R_GO.duty(0)
        self.R_BACK.duty(0)
        

    def move(self, v, w):
        """
        @param v: 线速度
        @param w: 转向角速度
        """
        v_l = v - w
        v_r = v + w
        
        # print(f"v_l: {v_l}, v_r: {v_r}")

        self.l_motor(v_l)
        self.r_motor(v_r)

if __name__ == '__main__':

    motor = Motor(3,4,2,1)

    while True:
        print("r_motor forward")
        motor.r_motor(200)
        sleep(2)    
        
        print("l_motor forward")
        motor.l_motor(100)
        sleep(2)
        
        print("stop")
        motor.stop()
        sleep(1)
        
        print("move")
        motor.move(200, 80) 
        sleep(5)

        print("stop")
        motor.stop()
        sleep(3)