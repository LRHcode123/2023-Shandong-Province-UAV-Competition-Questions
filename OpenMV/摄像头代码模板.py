#摄像头代码模板
import sensor, image, time, math, struct, pyb
import json
from pyb import LED,Timer
from struct import pack, unpack
from pyb import UART
uart = UART(3,500000)#初始化串口 波特率 500000
uart.init(500000, bits=8, parity=None, stop=1)

class Receive(object):
    uart_buf = []
    _data_len = 0
    _data_cnt = 0
    state = 0
R=Receive()

class Ctrl(object):
    WorkMode = 2   #工作模式
    IsDebug = 1     #不为调试状态时关闭某些图形显示等，有利于提高运行速度
    T_ms = 0
#类的实例化
Ctr=Ctrl()

Data = bytearray([0xAA,0xFF, 0xBB, 0x00,0x00,0x00,0x00, 0x00, 0x00, 0x00])

def UartSendData(timer):
    uart.write(Data)
    print(Data)
tim = Timer(2, freq=20)
tim.callback(UartSendData)

def ReceiveAnl(data_buf,num):
    #和校验
    sum = 0
    i = 0
    while i<(num-1):
        sum = sum + data_buf[i]
        i = i + 1
    sum = sum%256 #求余
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

#线检测数据打包
def LineDataPack(flag,angle,distance,crossflag,crossx,crossy,T_ms):#根据需要进行修改
    if (flag == 0):
        print("found: angle",angle,"  distance=",distance,"   线状态   未检测到直线")
    elif (flag == 1):
        print("found: angle",angle,"  distance=",distance,"   线状态   直线")
    elif (flag == 2):
        print("found: angle",angle,"  distance=",distance,"   线状态   左转")
    elif (flag == 3):
        print("found: angle",angle,"  distance=",distance,"   线状态   右转")

    line_data=bytearray([0xAA,0xFF,0xBB,0x00,flag,angle>>8,angle,distance>>8,distance,crossflag,crossx>>8,crossx,(-crossy)>>8,(-crossy),T_ms,0x00,0x00])
    lens = len(line_data)#数据包大小
    line_data[3] = lens-6;#有效数据个数
    i = 0
    sum = 0
    sum1 = 0
    #和校验
    while i<(lens-2):
        sum = sum + line_data[i]
        sum1 = sum1 + sum
        i = i+1
    line_data[lens-2] = sum;
    line_data[lens-1] = sum1;
    return line_data


class Line(object):
    flag = 0
    color = 0
    angle = 0
    distance = 0
    cross_x=0
    cross_y=0
    cross_flag=0
    dx = 0
    dy =0

class LineFlag(object):
    turn_left = 0
    turn_right = 0

LineFlag=LineFlag()
Line=Line()



sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
sensor.set_framesize(sensor.QVGA)#设置相机分辨率160*120
sensor.skip_frames(time=3000)#时钟
#sensor.set_auto_whitebal(False)#若想追踪颜色则关闭白平衡
sensor.set_hmirror(1)
sensor.set_vflip(1)
clock = time.clock()#初始化时钟

while(True):
    clock.tick()#时钟初始化
    #接收串口数据
    #UartReadBuffer()
    img = sensor.snapshot().lens_corr(1.8)
    Data = LineDataPack(Line.flag,Line.angle,Line.distance,Line.cross_flag,Line.cross_x,Line.cross_y,Ctr.T_ms)
    #计算程序运行频率
    if Ctr.IsDebug == 1:
        fps=int(clock.fps())
        Ctr.T_ms = (int)(1000/fps)
        print('fps',fps,'T_ms',Ctr.T_ms)

