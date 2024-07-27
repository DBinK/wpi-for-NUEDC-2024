from time import sleep
from machine import SoftI2C, Pin, PWM


class Motor:
    def __init__(self):
        self.L_GO   = PWM(Pin(21), freq=100)
        self.L_BACK = PWM(Pin(34), freq=100)
        self.R_GO   = PWM(Pin(35), freq=100)
        self.R_BACK = PWM(Pin(36), freq=100)

    def l_motor(self, speed):
        speed = int(max(0, min(speed, 1023)))
        if speed > 0:
            self.L_GO.duty(speed)
            self.L_BACK.duty(0)
        elif speed < 0:
            self.L_GO.duty(0)
            self.L_BACK.duty(-speed)
        else:
            self.L_GO.duty(0)

    def r_motor(self, speed):
        speed = int(max(0, min(speed, 1023)))
        if speed > 0:
            self.R_GO.duty(speed)
            self.R_BACK.duty(0)
        elif speed < 0:
            self.R_GO.duty(0)
            self.R_BACK.duty(-speed)
        else:
            self.R_GO.duty(0)

    def stop(self):
        self.l_motor(1)
        self.r_motor(1)

    def Motor_Control(self, pixel):
        if pixel == 0:
            self.l_motor(0)
            self.r_motor(0)
        else:
            self.l_motor(160 + pixel*0.4)
            self.r_motor(160 - pixel*0.4)

if __name__ == '__main__':
    motor = Motor()

    while True:
        print("r_motor forward")
        motor.r_motor(200)
        sleep(3)    
        
        print("l_motor forward")
        motor.l_motor(200)
        sleep(3)
        
        print("Motor_Control")
        motor.Motor_Control(200) 
        sleep(5)

        print("stop")
        motor.stop()
        sleep(3)