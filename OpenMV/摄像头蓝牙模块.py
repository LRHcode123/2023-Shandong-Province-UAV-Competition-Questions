#摄像头蓝牙模块
import sensor, image, time, math, struct, pyb
import json
from pyb import LED,Timer
from struct import pack, unpack
from pyb import UART
uart = UART(1,9600)#初始化串口 波特率 500000
#UART 1 RX -> P0 (PB15)
#UART 1 TX -> P1 (PB14)
uart.init(9600, bits=8, parity=None, stop=1)

class Receive(object):
    uart_buf = []
    _data_len = 0
    _data_cnt = 0
    state = 0
R=Receive()
class Ctrl(object):
    WorkMode = 0   #工作模式
    IsDebug = 1     #不为调试状态时关闭某些图形显示等，有利于提高运行速度
    T_ms = 0
#类的实例化
Ctr=Ctrl()

#串口数据解析
def ReceiveAnl(data_buf,num):
    #和校验
    sum = 0xFF
    if sum != data_buf[num-1]:
        return
    #和校验通过
    if data_buf[2]==0x05:
        #设置模块工作模式
        Ctr.WorkMode = data_buf[4]
#串口通信协议接收
def ReceivePrepare(data):
    if R.state==0:
        if data == 0xAA:#帧头
            R.uart_buf.append(data)
            R.state = 1
        else:
            R.state = 0
    elif R.state==1:
        if data == 0xAF:
            R.uart_buf.append(data)
            R.state = 2
        else:
            R.state = 0
    elif R.state==2:
        if data == 0x05:#功能字
            R.uart_buf.append(data)
            R.state = 3
        else:
            R.state = 0
    elif R.state==3:
        if data == 0x01:
            R.state = 4
            R.uart_buf.append(data)
        else:
            R.state = 0
    elif R.state==4:
        if data==1 or data==2 or data==3:
            R.uart_buf.append(data)
            R.state = 5
        else:
            R.state = 0
    elif R.state==5:
        R.state = 0
        R.uart_buf.append(data)
        ReceiveAnl(R.uart_buf,6)
        R.uart_buf=[]#清空缓冲区，准备下次接收数据
    else:
        R.state = 0

#读取串口缓存
def UartReadBuffer():
    i = 0
    Buffer_size = uart.any()
    while i<Buffer_size:
        ReceivePrepare(uart.readchar())
        i = i + 1
while(True):
    UartReadBuffer()
    if (Ctr.WorkMode==1):
        LED(1).on()
        time.sleep_ms(500)
        LED(1).off()
        time.sleep_ms(500)
    elif (Ctr.WorkMode==2):
        LED(2).on()
        time.sleep_ms(500)
        LED(2).off()
        time.sleep_ms(500)
    elif (Ctr.WorkMode==3):
        LED(3).on()
        time.sleep_ms(500)
        LED(3).off()
        time.sleep_ms(500)



