#巡找A点代码
import sensor, image, time, math, struct
from pyb import UART,LED,Timer

clock = time.clock()#初始化时钟

uart = UART(3,115200)#初始化串口 波特率 115200

led1 = LED(1)
led2 = LED(2)
led3 = LED(3)
led1.off()
led2.off()
led3.off()

IMG_WIDTH = 320
IMG_HEIGHT = 240


class Ctrl(object):
    WorkMode = 2   #工作模式
    IsDebug = 1     #不为调试状态时关闭某些图形显示等，有利于提高运行速度
    T_ms = 0   #每秒有多少帧
    Shirk=0 #窗口是否缩放

#类的实例化
Ctr=Ctrl()


#串口发送数据
def UartSendData(Data):
    print("write data",Data[0],Data[1],Data[2],Data[3],Data[4],Data[5],Data[6])
    uart.write(Data)


'''画矩形'''
def draw_blob(img,blob):
    if(blob!=None):
        img.draw_rectangle(blob.rect())#画矩形


#点检测数据打包
def DotDataPack(color,flag,x,y,T_ms,mode_flag):
    if(flag==1):
        print("found: x=",x,"  y=",-y)
    pack_data=bytearray([0xAA,0x29,0x05,mode_flag,0x00,color,flag,x>>8,x,(-y)>>8,(-y),T_ms,0x00])
    lens = len(pack_data)#数据包大小
    pack_data[4] = 7;#有效数据个数
    i = 0
    sum = 0
    #和校验
    while i<(lens-1):
        sum = sum + pack_data[i]
        i = i+1
    pack_data[lens-1] = sum;
    return pack_data


Green_threshold=(36, 75, -79, -36, -12, 55)
A_threshold=(0, 23, -19, 16, -19, 14)#(0, 30, -47, 0, 0, 39)
#A 家 (0, 21, -23, 10, -19, 25)
#A 场地 (13, 40, -36, 4, 5, 38)
class ADot(object):
    flag = 0
    color = 0
    x = 0
    y = 0
ADOT=ADot()

'''寻找A字'''
def find_A_blob(img):
    ADOT.flag=0;#重置没有找到
    blobs = img.find_blobs([A_threshold], merge=True)
    result=None
    #4.3  4.8 0.895   short/long
    #62 69  27 29
    last_sub=100.0
    max_blob=-100
    for blob in blobs:
        width=blob.w()
        height=blob.h()
        short_side=width if width<height else height
        long_side=width if width>height else height
        rate=short_side/long_side
        area=short_side*long_side
        #print("A",width,height,rate)
        #sub=math.fabs(0.7407-rate)
        side_limit=short_side>6 and short_side<68
        side_limit=side_limit and long_side>25 and long_side<68#and side_limit
        #if(sub<last_sub and side_limit and and find_AShape(img,blob) ):
        if(side_limit and area>max_blob):
            #last_sub=sub
            max_blob=area
            result=blob
        #draw_blob(img,blob)
    if result!=None:
        draw_blob(img,result)
        #更新要发送的数据
        print("SEND X Y: ",result.cx(),result.cy())
        ADOT.flag=1
        ADOT.x=result.cx()-int(IMG_WIDTH/2)
        ADOT.y=result.cy()-int(IMG_HEIGHT/2)
        LED(3).toggle()
    else:
        LED(3).off()
    #发送数据
    sendMessage()
    return result

'''发包'''
def sendMessage():
    #color,flag,x,y,T_ms
    pack=DotDataPack(0,ADOT.flag,ADOT.x,ADOT.y,Ctr.T_ms,0x44)
    UartSendData(pack)
    ADOT.flag=0#重置标志位

#---------------------------镜头初始化---------------------------#
sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
sensor.set_framesize(sensor.QVGA)#设置相机分辨率
sensor.skip_frames(time=2000)#时钟
#sensor.set_auto_whitebal(False)#若想追踪颜色则关闭白平衡
#sensor.set_auto_gain(False) # must be turned off for color tracking
#sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()#初始化时钟


while(True):
    clock.tick()
    img = sensor.snapshot()#拍一张图像
    find_A_blob(img)
    print(clock.fps())


