import time
from machine import UART
import bluetooth,ble_simple_peripheral


# 创建BLE对象
ble = bluetooth.BLE() # 构建BLE对象
peer = ble_simple_peripheral.BLESimplePeripheral(ble,name='WalnutPi')

def on_rx(msg):
    global text

    text = msg.decode("ascii")
    
    print("RX:",msg) #打印接收到的数据,数据格式为字节数组。
    peer.send("I got: ") 
    peer.send(text)
    
peer.on_write(on_rx) #从机接收回调函数，收到数据会进入on_rx函数。


while True:
    

