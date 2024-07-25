'''
实验名称：连接无线路由器
版本：v1.0
作者：WalnutPi
说明：编程实现连接路由器，将IP地址等相关信息打印出来。
'''
import network,time
from machine import Pin

# 释放所有GPIO, 断电重上电不再失控
def release_all_GPIO():
    for i in range(0, 47):
        try:
            Pin(i).off()
        except:
            pass

release_all_GPIO()


#WIFI连接函数
def WIFI_Connect():

    WIFI_LED=Pin(46, Pin.OUT) #初始化WIFI指示灯

    wlan = network.WLAN(network.STA_IF) #STA模式
    wlan.active(True)                   #激活接口
    start_time=time.time()              #记录时间做超时判断

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('DT46', '12345678') #输入WIFI账号密码

        while not wlan.isconnected():

            #LED闪烁提示
            WIFI_LED.value(1)
            time.sleep_ms(300)
            WIFI_LED.value(0)
            time.sleep_ms(300)

            #超时判断,15秒没连接成功判定为超时
            if time.time()-start_time > 5 :
                print('WIFI Connected Timeout!')
                break

    if wlan.isconnected():
        
        #LED点亮
        WIFI_LED.value(1)

        #串口打印信息
        print('network information:', wlan.ifconfig())

#执行WIFI连接函数
WIFI_Connect()
