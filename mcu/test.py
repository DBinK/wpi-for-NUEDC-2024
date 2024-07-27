from machine import Pin, PWM
import time

rg = PWM(Pin(35), freq=50) 
rb = PWM(Pin(36), freq=50)


rg.duty(0)
rb.duty(500)a