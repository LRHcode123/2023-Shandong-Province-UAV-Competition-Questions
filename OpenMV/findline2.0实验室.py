#巡线实验室版
import sensor, image, time, math, struct, json, mjpeg
from pyb import LED,Timer,UART


#----message
uart = UART(3,115200)#初始化串口 UART3波特率 500000

class Receive(object):
    uart_buf = []
    _data_len = 0
    _data_cnt = 0
    state = 0

R=Receive() #接收数据缓存对象

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
    print("Send Data: ","flag: ",flag,"angle",angle,"dis: ",distance,"cross_flag: ",crossflag,"crossx ",crossx,"crossy ",crossy);
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


IMG_WIDTH = 160
IMG_HEIGHT = 120
# 计算两直线的交点
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
        return (cross_x, cross_y)#返回交点
    else:#没有交点
        return None


'''计算两个直线的角度'''
def calculate_angle(line1, line2):
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle


'''图像中找最大的某个阈值色块'''
def find_maxSizeBlob_byThreshold(img,threshold):
    result=None
    blobs = img.find_blobs([threshold], pixels_threshold=3, area_threshold=3, merge=True, margin=5)
    for blob in blobs:
        if(result==None):
            result=blob
        elif(result.w()*result.h()<blob.w()*blob.h()):
            result=blob
    return result


'''画矩形'''
def draw_blob(img,blob):
    if(blob!=None):
        img.draw_rectangle(blob.rect())#画矩形

#----
#----line

green_threshold =(0, 23, -19, 16, -19, 14)# (40, 70, -47, -17, 3, 39)
#家 (22, 71, -46, -19, -7, 50)
#场地 (36, 75, -79, -36, -12, 55)(40, 73, -47, -19, 0, 34)
rad_to_angle = 57.29#弧度转度

class Line(object):
    flag = 0
    color = 0
    angle = 0
    distance = 0
    cross_x=0
    cross_y=0
    cross_flag=0

Line=Line()

def CalculateIntersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2()*line1.y1() - line1.x1()*line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1()*line2.y2()
    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:#两条线不平行，斜率不相等
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

#寻找每个感兴趣区里的指定色块并判断是否存在
def find_blobs_in_rois(img):
    '''
    在ROIS中寻找色块，获取ROI中色块的中心区域与是否有色块的信息
    '''
    IMG_WIDTH = img.width()
    IMG_HEIGHT = img.height()
    #正常ROI
    NORMAL_ROI = {
        'UL':       (20, 20, 60, 20),
        'UR':       (80, 20, 60, 20),
        'middle':   (20, 50, 120,20 ),
        'down':     (20, 80, 120, 20),
    }
    NORMAL_ROI_UR_MIN_AREA=60*20*0.6
    #mini ROI
    MINI_ROI={
        'UL':(40,30,40,15),
        'UR':(80,30,40,15),
        'middle':(40,55,80,15),
        'down':(40,75,80,15)
    }
    MINI_ROI_UR_MIN_AREA=40*15*0.6

    #根据状态字选择一种ROI模型
    ROIS=NORMAL_ROI
    ROIS_UR_MIN_AREA=NORMAL_ROI_UR_MIN_AREA
    UR_LEAF_W=45
    UR_LEAF_H=13


    if(Ctr.Shirk==1):
        ROIS=MINI_ROI
        ROIS_UR_MIN_AREA=MINI_ROI_UR_MIN_AREA


    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROIS.keys():  # 数值复位
        roi_blobs_result[roi_direct] = {
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }

    # 遍历所有ROI区域，寻找色块并取最大色块
    for roi_direct, roi in ROIS.items():

        if Ctr.IsDebug == 1:
            img.draw_rectangle(roi, color=(255,0,0))

        roix, roiy, roiw, roih = roi

        #寻找绿色色块
        blobs=img.find_blobs([green_threshold], roi=roi, merge=True, pixels_area=5)
        if len(blobs) == 0:
            continue
        # 取最大色块
        #largest_blob = max(blobs, key=lambda b: b.pixels())  #lambda函数：匿名函数冒号前面是参数，冒号后面是返回的值
        largest_blob = min(blobs, key=lambda b: b.x())  #lambda函数：匿名函数冒号前面是参数，冒号后面是返回的值
        #控制右上色块的大小
        if(largest_blob==None or ((largest_blob.w()<UR_LEAF_W or largest_blob.h()<UR_LEAF_H) and roi_direct=='UR')):
            continue
        x,y,width,height = largest_blob[:4]
        print("max blob: ", largest_blob[:4])

        if(roi_direct=='middle' or roi_direct=='UL' or roi_direct=='down'):
            roi_blobs_result[roi_direct]['cx'] = x+width
        roi_blobs_result[roi_direct]['cy'] = y
        roi_blobs_result[roi_direct]['blob_flag'] = True

        if Ctr.IsDebug == 1:
            img.draw_rectangle((x,y,width, height), color=(0,255,255))


    # 左右都有，中下也有
    if roi_blobs_result['UL']['blob_flag'] and roi_blobs_result['UR']['blob_flag'] \
        and roi_blobs_result['middle']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        # 右转
        Line.flag = 3
    elif roi_blobs_result['UL']['blob_flag'] and roi_blobs_result['middle']['blob_flag'] \
        and roi_blobs_result['down']['blob_flag']:
        # 直行
        Line.flag = 1
    elif roi_blobs_result['middle']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        # 左转
        Line.flag = 2
    elif roi_blobs_result['UL']['blob_flag']:
        # 刚结束左转 直行
        Line.flag = 1
    else:
        # 未检测到
        Line.flag = 0

    if Ctr.IsDebug == 1:
        print("Line.flag: ", Line.flag)

    #图像上显示检测到的直角类型
    turn_type = 'N' # 不转
    if Line.flag == 2:
        turn_type = 'L' # 左转
    elif Line.flag == 3:
        turn_type = 'R' # 右转

    #计算角度
    CX1 = roi_blobs_result['UL']['cx']
    CX2 = roi_blobs_result['middle']['cx']
    CX3 = roi_blobs_result['down']['cx']
    CY1 = roi_blobs_result['UL']['cy']
    CY2 = roi_blobs_result['middle']['cy']
    CY3 = roi_blobs_result['down']['cy']
    if  Line.flag:
        Line.distance = CX2 - int(IMG_WIDTH/2)
    else:
        Line.distance = 0


    # 转弯
    #if Line.flag==2 or Line.flag==3:
        #Line.angle = math.atan((CX2-CX3)/(CY2-CY3))* rad_to_angle
        #Line.angle = int(Line.angle)
    # 直走
    if Line.flag==1 and  roi_blobs_result['middle']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        Line.angle = math.atan((CX2-CX3)/(CY2-CY3))* rad_to_angle
        Line.angle = int(Line.angle)
    elif roi_blobs_result['UL']['blob_flag']:
        Line.angle = math.atan((CX1-CX2)/(CY1-CY2))* rad_to_angle
        Line.angle = int(Line.angle)
    else:
        Line.angle = 0

    if Ctr.IsDebug == 1:
        img.draw_string(0, 0, turn_type, color=(255,255,255))
        img.draw_string(int(IMG_WIDTH/8), 0, str(Line.angle), color=(255,255,255))


#线检测
def find_line():
    # 拍摄图片
    img = sensor.snapshot()
    find_blobs_in_rois(img)
    #寻线数据打包发送
    UartSendData(LineDataPack(Line.flag,Line.angle,Line.distance,Line.cross_flag,Line.cross_x,Line.cross_y,Ctr.T_ms))
    return Line.flag

sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
sensor.set_framesize(sensor.QQVGA)#设置相机分辨率
sensor.skip_frames(time=2000)#时钟
#sensor.set_auto_gain(False) # must be turned off for color tracking
#sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()#初始化时钟


while(True):
    clock.tick()
    img = sensor.snapshot()#拍一张图像
    find_line()
    print(clock.fps())
