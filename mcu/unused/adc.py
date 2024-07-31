'''
实验名称：ADC-电压测量
版本：v1.0
作者：WalnutPi
说明：通过对ADC数据采集，转化成电压在显示屏上显示。ADC精度12位（0~4095），测量电压0-3.3V。
'''

#导入相关模块
from machine import Pin,ADC,Timer
import time

#构建ADC对象
adc1 = ADC(Pin(0)) #使用引脚9
adc1.atten(ADC.ATTN_11DB) #开启衰减器，测量量程增大到3.3V
#构建ADC对象
adc2 = ADC(Pin(1)) #使用引脚9
adc2.atten(ADC.ATTN_11DB) #开启衰减器，测量量程增大到3.3V

def ADC_Test():

    #打印ADC原始值
    # print(adc.read())
    

    adc1_value = '%.2f'%(adc1.read()/4095*3.3)
    adc2_value = '%.2f'%(adc2.read()/4095*3.3)

    #计算电压值，获得的数据0-4095相当于0-3.3V，（'%.2f'%）表示保留2位小数
    print(f'adc2_value = {adc2_value}, adc1_value = {adc1_value}')

print("开始")

while 1:
    ADC_Test()
    time.sleep(0.01)

tim = Timer(0)
tim.init(period=100, mode=Timer.PERIODIC, callback=ADC_Test) #周期300ms
