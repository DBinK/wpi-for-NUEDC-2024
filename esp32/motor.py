from time import sleep
from machine import SoftI2C, Pin, PWM


class Motor:
    def __init__(self):
        self.L_GO   = PWM(Pin(21), freq=100)
        self.L_BACK = PWM(Pin(34), freq=100)
        self.R_GO   = PWM(Pin(35), freq=100)
        self.R_BACK = PWM(Pin(36), freq=100)

    def L_Motor(self, speed):
        speed = int(max(0, min(speed, 1023)))
        if speed > 0:
            self.L_GO.duty(speed)
            self.L_BACK.duty(0)
        elif speed < 0:
            self.L_GO.duty(0)
            self.L_BACK.duty(-speed)
        else:
            self.L_GO.duty(0)

    def R_Motor(self, speed):
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
        self.L_Motor(1)
        self.R_Motor(1)

    def Motor_Control(self, pixel):
        if pixel == 0:
            self.L_Motor(0)
            self.R_Motor(0)
        else:
            self.L_Motor(160 + pixel*0.4)
            self.R_Motor(160 - pixel*0.4)

if __name__ == '__main__':
    motor = Motor()

    while True:
        print("R_Motor forward")
        motor.R_Motor(200)
        sleep(3)    
        
        print("L_Motor forward")
        motor.L_Motor(200)
        sleep(3)
        
        print("Motor_Control")
        motor.Motor_Control(200) 
        sleep(5)

        print("stop")
        motor.stop()
        sleep(3)