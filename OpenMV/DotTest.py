#巡点模式测试代码
import sensor, image, time, math, struct
import json
from pyb import LED,Timer
from struct import pack, unpack
from pyb import UART
from image import SEARCH_EX, SEARCH_DS
texty=(12, 46, -40, 85, -29, 108)
uart = UART(3,500000)#初始化串口 波特率 500000
uart.init(500000, bits=8, parity=None, stop=1)

class Receive(object):
    uart_buf = []
    _data_len = 0
    _data_cnt = 0
    state = 0

R=Receive()
# WorkMode=1为寻点模式
# WorkMode=2为寻线模式 包括直线 转角
class Ctrl(object):
    WorkMode = 2   #工作模式
    IsDebug = 1     #不为调试状态时关闭某些图形显示等，有利于提高运行速度
    T_ms = 0
#类的实例化
Ctr=Ctrl()

def UartSendData(Data):
    uart.write(Data)

#串口数据解析
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
    if data_buf[4]==0x06:
        #设置模块工作模式
        Ctr.WorkMode = data_buf[5]
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
        if data == 0x05:
            R.uart_buf.append(data)
            R.state = 3
        else:
            R.state = 0
    elif R.state==3:
        if data == 0x01:#功能字
            R.state = 4
            R.uart_buf.append(data)
        else:
            R.state = 0
    elif R.state==4:
        if data == 0x06:#数据个数
            R.state = 5
            R.uart_buf.append(data)
            R._data_len = data
        else:
            R.state = 0
    elif R.state==5:
        if data==1 or data==2 or data==3:
            R.uart_buf.append(data)
            R.state = 6
        else:
            R.state = 0
    elif R.state==6:
        R.state = 0
        R.uart_buf.append(data)
        ReceiveAnl(R.uart_buf,7)
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

#点检测数据打包
def DotDataPack(color,flag,x,y,T_ms):
    print("found: x=",x,"  y=",-y)
    pack_data=bytearray([0xAA,0xFF,0XAA,0x00,color,flag,x>>8,x,(-y)>>8,(-y),T_ms,0x00,0x00])
    lens = len(pack_data)#数据包大小
    pack_data[3] = 7;#有效数据个数
    i = 0
    sum = 0
    sum1 = 0
    #和校验
    while i<(lens-2):
        sum = sum + pack_data[i]
        sum1 = sum1 + sum
        i = i+1
    pack_data[lens-2] = sum;
    pack_data[lens-1] = sum1;
    return pack_data

#线检测数据打包
def LineDataPack(flag,angle,distance,crossflag,crossx,crossy,T_ms):
    if (flag == 0):
        print("found: angle",angle,"  distance=",distance,"   线状态   未检测到直线")
    elif (flag == 1):
        print("found: angle",angle,"  distance=",distance,"   线状态   直线")
    elif (flag == 2):
        print("found: angle",angle,"  distance=",distance,"   线状态   左转")
    elif (flag == 3):
        print("found: angle",angle,"  distance=",distance,"   线状态   右转")

    line_data=bytearray([0xAA,0x29,0x05,0x42,0x00,flag,angle>>8,angle,distance>>8,distance,crossflag,crossx>>8,crossx,(-crossy)>>8,(-crossy),T_ms,0x00])
    lens = len(line_data)#数据包大小
    line_data[4] = 11;#有效数据个数
    i = 0
    sum = 0
    #和校验
    while i<(lens-1):
        sum = sum + line_data[i]
        i = i+1
    line_data[lens-1] = sum;
    return line_data
#用户数据打包
def UserDataPack(data0,data1,data2,data3,data4,data5,data6,data7,data8,data9):
    UserData=bytearray([0xAA,0x05,0xAF,0xF1,0x00
                        ,data0,data1,data2>>8,data2,data3>>8,data3
                        ,data4>>24,data4>>16,data4>>8,data4
                        ,data5>>24,data5>>16,data5>>8,data5
                        ,data6>>24,data6>>16,data6>>8,data6
                        ,data7>>24,data7>>16,data7>>8,data7
                        ,data8>>24,data8>>16,data8>>8,data8
                        ,data9>>24,data9>>16,data9>>8,data9
                        ,0x00])
    lens = len(UserData)#数据包大小
    UserData[4] = lens-6;#有效数据个数
    i = 0
    sum = 0
    #和校验
    while i<(lens-1):
        sum = sum + UserData[i]
        i = i+1
    UserData[lens-1] = sum;
    return UserData
Red_threshold =(65, 90, 53, 27, -18, 4)#  寻色块用 红色
Blue_threshold =(0, 48, -20, 59, -66, -28)#  寻色块用 蓝色
Green_threshold =(30, 100, -64, -8, -32, 32)#  寻色块用 蓝色

class Dot(object):
    flag = 0
    color = 0
    x = 0
    y = 0

Dot=Dot()


#色块识别函数
#定义函数：找到画面中最大的指定色块
def FindMax(blobs):
    max_size=1
    if blobs:
        max_blob = 0
        for blob in blobs:
            blob_size = blob.w()*blob.h()
            if ( (blob_size > max_size) & (blob_size > 100)   ) :#& (blob.density()<1.2*math.pi/4) & (blob.density()>0.8*math.pi/4)
                if ( math.fabs( blob.w() / blob.h() - 1 ) < 2.0 ) :
                    max_blob=blob
                    max_size = blob.w()*blob.h()
        return max_blob

def LineFilter(src, dst):
  for i in range(0, len(dst), 1):
      dst[i] = src[i<<1]
testdot1=(37, 51, 44, 96, -7, 72)
testdot2=(11, 23, 8, -8, -7, 32)
testdot3=(57, 67, 2, 13, -38, -6)
#点检测
def DotCheck():
    img = sensor.snapshot(line_filter = LineFilter)#拍一张图像
    red_blobs = img.find_blobs([testdot2], pixels_threshold=3, area_threshold=3, merge=True, margin=5)#识别红色物体
    max_blob=FindMax(red_blobs)#找到最大的那个
    if max_blob:
        img.draw_cross(max_blob.cx(), max_blob.cy())#物体中心画十字
        img.draw_rectangle(max_blob.rect())#画圈
        #获取坐标并转换为+-200
        Dot.x = max_blob.cx()-80
        Dot.y = max_blob.cy()-60
        Dot.flag = 1
        #LED灯闪烁
        LED(3).toggle()
        #LED灯闪烁
        LED(2).toggle()
    else:
        #Dot.x = 0
        #Dot.y = 0
        Dot.flag = 0
        LED(2).off()
        LED(3).off()
    UartSendData(DotDataPack(Dot.color,Dot.flag,Dot.x,Dot.y,Ctr.T_ms))
    return Dot.flag
    #串口发送数据给飞控
#pack_data = bytearray([0xAA,0xFF, 0xAA, 0x00, 0xFF, 0x00,0x00,0x00,0x00, 0x00, 0x00, 0x00, 0x00])
#def uartsend(timer):
    #uart.write(pack_data)
    #print(pack_data)
#tim = Timer(2, freq=20)
#tim.callback(uartsend)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
sensor.set_framesize(sensor.QQVGA)#设置相机分辨率160*120
sensor.skip_frames(time=3000)#时钟
sensor.set_auto_whitebal(False)#若想追踪颜色则关闭白平衡
sensor.set_hmirror(1)
sensor.set_vflip(1)
clock = time.clock()#初始化时钟

#主循环
while(True):
    clock.tick()#时钟初始化
    #接收串口数据
    #UartReadBuffer()
    #if Message.Ctr.WorkMode==1:#点检测
    DotCheck()
    #elif (Message.Ctr.WorkMode==2):#线检测
    #LineCheck()
    #用户数据发送
    #Message.UartSendData(Message.UserDataPack(127,127,32767,32767,65536,65536,65536,65536,65536,65536))
    #计算程序运行频率
    if Ctr.IsDebug == 1:
        fps=int(clock.fps())
        Ctr.T_ms = (int)(1000/fps)
        print('fps',fps,'T_ms',Ctr.T_ms)
