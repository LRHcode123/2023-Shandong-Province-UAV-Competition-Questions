#----start 起始点监测
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

#家参数(0, 21, -17, 15, -31, 13)
#场地参数(2, 26, -33, 16, -22, 31)
startPoint_threshold =(2, 26, -33, 16, -22, 31)
CROSS_MIN=10
CROSS_MAX=90

# WorkMode=1为寻点模式
# WorkMode=2为寻线模式 包括直线 转角
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


class StartDot(object):
    flag = 0
    color = 0
    x = 0
    y = 0
STARTDOT=StartDot()


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



'''寻找十字起点'''
def find_start_point_blob(img):
    #重置标志位
    STARTDOT.flag=0;
    blobs = img.find_blobs([startPoint_threshold], pixels_threshold=3, area_threshold=3, merge=True, margin=5)
    result=None
    last_sub=2.0
    for blob in blobs:
        width=blob.w()
        height=blob.h()
        rate=width/height
        size_limit=width>CROSS_MIN and width<CROSS_MAX and height>CROSS_MIN and height<CROSS_MAX
        sub=abs(1.0-rate)
        if(last_sub>sub and size_limit):
            print(width,height,rate)#
            last_sub=sub
            result=blob
    #十字检测
    if result!=None:
        cross_test_result,point=find_crossShape(img,result.rect())
        print("cross_test_result",cross_test_result,point)
        if(cross_test_result):
            draw_blob(img,result)
            img.draw_cross(point[0],point[1],5,color=[0,255,0])
            STARTDOT.flag=1
            STARTDOT.x=point[0]-int(IMG_WIDTH/2)
            STARTDOT.y=point[1]-int(IMG_HEIGHT/2)
    sendMessage()
    return result


'''测试十字'''
def find_crossShape(img,ROI):
    result=False
    result_point=(-1,-1)
    if(ROI==None):
        return result,result_point
    lines=img.find_lines(roi=ROI, theta_margin = 25, rho_margin = 25)
    line_num = len(lines)
    for i in range(line_num -1):
            for j in range(i, line_num):
                # 判断两个直线之间的夹角是否为直角
                angle = calculate_angle(lines[i], lines[j])
                print("Angle",angle)
                # 判断角度是否在阈值范围内
                if not(angle >= 83 and angle <=  90):
                    continue#不在区间内
                intersect_pt = CalculateIntersection(lines[i], lines[j])
                if intersect_pt is None:
                    continue
                #有交点
                x, y = intersect_pt
                #不在图像范围内
                if not(x >= 0 and x < IMG_WIDTH and y >= 0 and y < IMG_HEIGHT):
                    # 交点如果没有在画面中
                    continue
                result_point=(x,y)
                return (True,result_point)
    return (result,result_point)

'''找圆形'''
def find_cirlce_method(img):
    STARTDOT.flag=0
    for c in img.find_circles(threshold = 3500, x_margin = 10, y_margin = 10, r_margin = 10,r_min = 2, r_max = 100, r_step = 2):
        #十字检测
        leaf_radius=int(c.r()/2.0);
        ROI=[c.x()-leaf_radius,c.y()-leaf_radius,c.x()+leaf_radius,c.y()+leaf_radius]
        cross_test_result,point=find_crossShape(img,ROI)
        print("cross_test_result",cross_test_result,point)
        if(cross_test_result):
            img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))
            STARTDOT.flag=1
            STARTDOT.x=c.x()-int(IMG_WIDTH/2)
            STARTDOT.y=c.y()-int(IMG_HEIGHT/2)
            print(c)
    sendMessage()


'''发包'''
def sendMessage():
    #color,flag,x,y,T_ms
    pack=DotDataPack(0,STARTDOT.flag,STARTDOT.x,STARTDOT.y,Ctr.T_ms,0x43)
    UartSendData(pack)
    STARTDOT.flag=0#重置标志位

#----
#---------------------------镜头初始化---------------------------#
sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
sensor.set_framesize(sensor.QVGA)#设置相机分辨率
sensor.skip_frames(time=2000)#时钟
#sensor.set_auto_gain(False) # must be turned off for color tracking
#sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()#初始化时钟


while(True):
    clock.tick()
    img = sensor.snapshot()#拍一张图像
    find_start_point_blob(img)
    print(clock.fps())
