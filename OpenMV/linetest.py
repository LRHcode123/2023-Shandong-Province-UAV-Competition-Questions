#巡线模式测试代码
import sensor, image, time, math, struct,pyb
import json
from pyb import LED,Timer
from struct import pack, unpack
from pyb import UART
texty=(12, 45, -56, 55, -29, 108)
uart = UART(3,500000)#初始化串口 波特率 500000
led1 = pyb.LED(1)
led = pyb.LED(2)
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
        if data == 0x02:#功能字
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

    line_data=bytearray([0xAA,0xFF,0xBB,0x00,flag,angle>>8,angle,distance>>8,distance,crossflag,crossx>>8,crossx,(-crossy)>>8,(-crossy),T_ms,0x00,0x00])
    lens = len(line_data)#数据包大小
    line_data[3] = 11;#有效数据个数
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
Black_threshold =(4, 31, -20, 49, -36, 58)# 寻线 用  黑色
rad_to_angle = 57.29#弧度转度
IMG_WIDTH = 160
IMG_HEIGHT = 120
# 取样窗口
ROIS = {
    'down':   (0, 105, 160, 15), # 横向取样-下方       1
    'middle': (0, 52,  160, 15), # 横向取样-中间       2
    'up':     (0,  0,  160, 15), # 横向取样-上方       3
    'left':   (0,  0,  15, 120), # 纵向取样-左侧       4
    'right':  (145,0,  15, 120), # 纵向取样-右侧       5
    'All':    (0,  0,  160,120), # 全画面取样-全画面    6
}
class Line(object):
    flag = 0
    color = 0
    angle = 0
    distance = 0
    cross_x=0
    cross_y=0
    cross_flag=0

class LineFlag(object):
    turn_left = 0
    turn_right = 0

LineFlag=LineFlag()
Line=Line()
#计算两直线交点坐标
def CalculateIntersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2()*line1.y1() - line1.x1()*line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1()*line2.y2()
    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1*c2-b2*c1)/(a1*b2-a2*b1))
        cross_y = int((c1*a2-c2*a1)/(a1*b2-a2*b1))

        Line.cross_flag = 1
        Line.cross_x = cross_x-80
        Line.cross_y = cross_y-60
        img.draw_cross(cross_x,cross_y,5,color=[255,0,0])
        return (cross_x, cross_y)
    else:
        Line.cross_flag = 0
        Line.cross_x = 0
        Line.cross_y = 0
        return None
def calculate_angle(line1, line2):
    '''
    利用四边形的角公式， 计算出直线夹角
    '''
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle
def find_interserct_lines(lines, angle_threshold=(10,90), window_size=None):
    '''
    根据夹角阈值寻找两个相互交叉的直线， 且交点需要存在于画面中
    '''
    line_num = len(lines)
    for i in range(line_num -1):
        for j in range(i, line_num):
            # 判断两个直线之间的夹角是否为直角
            angle = calculate_angle(lines[i], lines[j])
            # 判断角度是否在阈值范围内
            if not(angle >= angle_threshold[0] and angle <=  angle_threshold[1]):
                continue

            # 判断交点是否在画面内
            if window_size is not None:
                # 获取窗口的尺寸 宽度跟高度
                win_width, win_height = window_size
                # 获取直线交点
                intersect_pt = CalculateIntersection(lines[i], lines[j])
                if intersect_pt is None:
                    # 没有交点
                    Line.cross_x = 0
                    Line.cross_y = 0
                    Line.cross_flag = 0
                    continue
                x, y = intersect_pt
                if not(x >= 0 and x < win_width and y >= 0 and y < win_height):
                    # 交点如果没有在画面中
                    Line.cross_x = 0
                    Line.cross_y = 0
                    Line.cross_flag = 0
                    continue
            return (lines[i], lines[j])
    return None

blackline=(5, 26, -29, 12, -14, 15)
#寻找每个感兴趣区里的指定色块并判断是否存在
def find_blobs_in_rois(img):
    '''
    在ROIS中寻找色块，获取ROI中色块的中心区域与是否有色块的信息
    '''
    global ROIS

    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROIS.keys():#数值复位
        roi_blobs_result[roi_direct] = {
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }
    for roi_direct, roi in ROIS.items():
        blobs=img.find_blobs([blackline], roi=roi, merge=True, pixels_area=10)
        if len(blobs) == 0:
            continue

        largest_blob = max(blobs, key=lambda b: b.pixels())
        x,y,width,height = largest_blob[:4]

        if not(width >=3 and width <= 45 and height >= 3 and height <= 45):
            # 根据色块的长宽进行过滤
            continue

        roi_blobs_result[roi_direct]['cx'] = largest_blob.cx()
        roi_blobs_result[roi_direct]['cy'] = largest_blob.cy()
        roi_blobs_result[roi_direct]['blob_flag'] = True
        img.draw_rectangle((x,y,width, height), color=(0,255,255))

    # 判断是否需要左转与右转
    LineFlag.turn_left = False#先清除标志位
    LineFlag.turn_right = False
    if (not roi_blobs_result['up']['blob_flag'] ) and roi_blobs_result['down']['blob_flag'] and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        if roi_blobs_result['left']['blob_flag']:
            LineFlag.turn_left = True
        if roi_blobs_result['right']['blob_flag']:
            LineFlag.turn_right = True
    if (roi_blobs_result['up']['blob_flag']and roi_blobs_result['middle']['blob_flag']and roi_blobs_result['down']['blob_flag']):
        Line.flag = 1#直线
    elif LineFlag.turn_left:
        Line.flag = 2#左转
    elif LineFlag.turn_right:
        Line.flag = 3#右转
    elif (not roi_blobs_result['down']['blob_flag'] ) and roi_blobs_result['up']['blob_flag']and ( roi_blobs_result['right']['blob_flag'] or roi_blobs_result['left']['blob_flag'])and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        Line.flag = 1#左右转后直线
    else:
        Line.flag = 0#未检测到
    #图像上显示检测到的直角类型
    turn_type = 'N' # 啥转角也不是
    if LineFlag.turn_left:
        turn_type = 'L' # 左转
    elif LineFlag.turn_right:
        turn_type = 'R' # 右转
    img.draw_string(0, 0, turn_type, color=(255,255,255))
    #计算角度
    CX1 = roi_blobs_result['up']['cx']
    CX2 = roi_blobs_result['middle']['cx']
    if  Line.flag:
        Line.distance = CX2-80
    else:
        Line.distance = 0
    CX3 = roi_blobs_result['down']['cx']
    CY1 = roi_blobs_result['up']['cy']
    CY2 = roi_blobs_result['middle']['cy']
    CY3 = roi_blobs_result['down']['cy']
    if LineFlag.turn_left or LineFlag.turn_right:
        Line.angle = math.atan((CX2-CX3)/(CY2-CY3))* rad_to_angle
        Line.angle = int(Line.angle)
    elif Line.flag==1 and (roi_blobs_result['down']['blob_flag'] and roi_blobs_result['up']['blob_flag'] ):
        Line.angle = math.atan((CX1-CX3)/(CY1-CY3))* rad_to_angle
        Line.angle = int(Line.angle)
    elif (not roi_blobs_result['down']['blob_flag'] ) and roi_blobs_result['up']['blob_flag']and ( roi_blobs_result['right']['blob_flag'] or roi_blobs_result['left']['blob_flag'])and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        Line.angle = math.atan((CX1-CX2)/(CY1-CY2))* rad_to_angle
        Line.angle = int(Line.angle)
    else:
        Line.angle = 0

#线检测
def LineCheck():
    # 拍摄图片
    global img
    img = sensor.snapshot()
    lines = img.find_lines(threshold=1000, theta_margin = 50, rho_margin = 50)
    #LED灯闪烁
    LED(3).toggle()
    #LED灯闪烁
    LED(2).toggle()
    if not lines:
        Line.cross_x=Line.cross_y= Line.cross_flag=0
        LED(2).off()
        LED(3).off()
    # 寻找相交的点 要求满足角度阈值
    find_interserct_lines(lines, angle_threshold=(45,90), window_size=(IMG_WIDTH, IMG_HEIGHT))
    find_blobs_in_rois(img)
    print('交点坐标',Line.cross_x,-Line.cross_y, Line.cross_flag)
    #寻线数据打包发送
    UartSendData(LineDataPack(Line.flag,Line.angle,Line.distance,Line.cross_flag,Line.cross_x,Line.cross_y,Ctr.T_ms))
    return Line.flag


sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
sensor.set_framesize(sensor.QQVGA)#设置相机分辨率160*120
sensor.skip_frames(time=3000)#时钟
sensor.set_auto_whitebal(False)#若想追踪颜色则关闭白平衡
sensor.set_hmirror(1)
sensor.set_vflip(1)
clock = time.clock()#初始化时钟
#led1.on()
#主循环
while(True):
    clock.tick()#时钟初始化

    #接收串口数据
    #UartReadBuffer()
    LineCheck()
    #if Ctr.WorkMode==1:#点检测

    #DotCheck()
    #if (Ctr.WorkMode==2):#线检测
        #led.on()
    #计算程序运行频率
    if Ctr.IsDebug == 1:
        fps=int(clock.fps())
        Ctr.T_ms = (int)(1000/fps)
        print('fps',fps,'T_ms',Ctr.T_ms)
