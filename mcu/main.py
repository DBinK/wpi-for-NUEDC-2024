import bluetooth
import machine
from neopixel import NeoPixel
from ble_simple_peripheral import BLESimplePeripheral
import motion

class LEDController:
    def __init__(self, pin_number, pixel_count):
        self.pin = machine.Pin(pin_number, machine.Pin.OUT)
        self.np = NeoPixel(self.pin, pixel_count)
        self.colors = [
            (255, 0, 0),  # 红色
            (255, 165, 0),  # 橙色
            (255, 255, 0),  # 黄色
            (0, 255, 0),  # 绿色
            (0, 255, 255),  # 青色
            (0, 0, 255),  # 蓝色
            (128, 0, 128),  # 紫色
            (255, 255, 255),  # 白色
        ]
        self.timer = machine.Timer(2)
        self.timer.init(period=500, mode=machine.Timer.PERIODIC, callback=self.rgb_flow)

    def rgb_flow(self, _):
        global colors
        for i in range(len(self.colors)):
            self.np[i] = self.colors[i]
        self.np.write()
        self.colors.append(self.colors.pop(0))

class BluetoothController:
    def __init__(self, name='WPi-Car'):
        self.ble = bluetooth.BLE()
        self.ble_client = BLESimplePeripheral(self.ble, name=name)
        self.car_sw = 0
        self.rotate_sw = 0
        self.rotate_mode = 0
        self.ble_client.on_write(self.on_rx)
        self.motion = motion.RobotController()
        self.motion.stop()

    def on_rx(self, text):

        go_speed = 900
        turn_speed = 500
        
        try:        
            # print("RX:", text) #打印接收到的数据
            
            # 回传数据给主机。
            self.ble_client.send("I got: ")
            self.ble_client.send(text)
            
            hex_data = ['{:02x}'.format(byte) for byte in text]
            
            print(hex_data)
            
            if len(hex_data) > 6:
                
                if (hex_data[6] == '00' or hex_data[7] == '00') and self.rotate_sw == 0 and self.car_sw == 0:
                    self.motion.stop()

                if hex_data[6] == '01':  # up
                    self.motion.go_forward(go_speed)
                    
                if hex_data[6] == '02':  # down
                    self.motion.go_backward(go_speed)
                    
                if hex_data[6] == '04':  # left
                    self.motion.go_left(go_speed)
                    
                if hex_data[6] == '08':  # right
                    self.motion.go_right(go_speed)
                    
                if hex_data[5] == '04':  # y
                    self.motion.move(700, 200, -500)
                    
                if hex_data[5] == '20':  # x
                    self.motion.move(700, -200, 500)

                if hex_data[5] == '08':  # b
                    if self.rotate_mode == 0 :
                        self.motion.move(0, 0, -500)
                    elif self.rotate_mode == 1 :
                        self.motion.move(500, -600, -150)
                    
                if hex_data[5] == '10':  # a
                    if self.rotate_mode == 0 :
                        self.motion.move(0, 0, 500)
                    elif self.rotate_mode == 1 :
                        self.motion.move(500, 600, 150)
                    
                if hex_data[5] == '02':  # select
                
                    if self.rotate_sw == 0:
                        self.rotate_sw = 1 
                        self.motion.turn_right(go_speed)

                    elif self.rotate_sw == 1:
                        self.rotate_sw = 2
                        self.motion.turn_left(go_speed)
                        
                    else:
                        self.rotate_sw = 0
                        self.motion.stop()
                        
                    print(f"开关小陀螺: {self.rotate_sw}")
                    
                if hex_data[5] == '01':  # start
                    
                    if self.rotate_mode == 0 :
                        self.rotate_mode = 1 
                    else:
                        self.rotate_mode = 0
                    
                    print(f"B/A键转弯的模式: {self.rotate_mode}")
                    """ ble_client.on_write(None)
                    sys.exit() """
                    
        except (OSError, RuntimeError) as e:
            print(f"错误原因：{e}")
            # ble_client.on_write(None)
            # sys.exit()

class WalnutPiCar:
    def __init__(self):
        self.led_controller = LEDController(12, 8)
        self.bluetooth_controller = BluetoothController()

    def main(self):
        # 主循环或初始化代码可以放在这里
        pass

if __name__ == "__main__":
    wpicar = WalnutPiCar()
    wpicar.main()
