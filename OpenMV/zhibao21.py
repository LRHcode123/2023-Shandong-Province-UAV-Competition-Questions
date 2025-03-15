# Untitled - By: hgf - 周四 11月 4 2021
import sensor
import image
import time
import network
import usocket
import sys
import math
from pyb import UART
from pyb import LED
from pyb import Pin
'''
Type:
    199:A
    200:green
    201:line
    202:直角
    203:起飞、降落点
'''
p_out = Pin('P7', Pin.OUT_PP)
grey_threshold=(69, 83, -15, 21, -37, 23)#灰色阈值
white_threshold=(97,103,-5,5,-5,5)
green_threshold=(56, 89, -47, -5, 22, 46)
black_threshold=(0, 39, -46, 16, -8, 56)
thresholds=[
green_threshold
]
area_tmp=[0,0]
illroi=(84,50,12,14)#正下方一小块
red_led = LED(1)
green_led = LED(2)
blue_led = LED(3)
ir_led = LED(4)
p_out.low()#激光打点置低位
t=0
i=0
look_a=0
uart=UART(1,115200)
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
def UART_Send(FormType, Location0, Location1, frame_type=0, area=65535, width=0):   #通信协议
    fHead = bytes([170,170])                                                        #帧头为AA
    Frame_End = [85, 85]
    fFormType_tmp = [FormType]
    prame = bytes(0)
    # 计算区域值
    area_tmp[0] = area & 0xFF #area也是十六位，但其实可以不是面积，啥都行
    area_tmp[1] = area >> 8
    area = bytes(area_tmp)
    fFormType = bytes(fFormType_tmp)
    fLocation0 = bytes([Location0])#十六位
    fLocation1 = bytes([Location1])
    fEnd = bytes(Frame_End)                                                         #帧尾为0x55
    fwidth = bytes([width])
    if frame_type == 0:
        FrameBuffe = fHead + fFormType + fLocation0 + fLocation1 + fEnd
    elif frame_type == 1:
        FrameBuffe = fHead + fFormType + fLocation0 + fLocation1 + area + fwidth + fEnd
        #print(FrameBuffe)
        pass
    return FrameBuffe
def jiguang():          #激光打点
    time0=time.ticks_ms()
    if(time0%1000<100):
        #打点0.1S
        p_out.high()
    else:
        p_out.low()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
while True:
    t=t+1
    clock.tick()
    time0=time.ticks_ms()
    img = sensor.snapshot().lens_corr(1.8)  #消除鱼眼畸变

    for l in img.find_lines(x_stride=1,y_stride=60,roi=(92,0,30,120),threshold=40,theta_margin=15,rho_margin=15):
        if(l.theta()<10 or l.theta()>170):  #寻找横线
            #img.draw_line(l.line(), color = (255, 0, 0))
            print(l.theta())
            Type=201
            p0=l.theta()
            p1=0
            area=0
            #uart.write(UART_Send(Type, p0, p1, area = area, frame_type=1))
    for l in img.find_lines(x_stride=50,y_stride=5,roi=(0,0,160,40),threshold=40,theta_margin=15,rho_margin=15):
        if(l.theta()>80 and l.theta()<100): #寻找竖线
            #img.draw_line(l.line(), color = (0, 255, 0))
            print(l.theta())
            Type=202
            p0=l.theta()#左上右下是大，左下右上是小
            print(p0)
            p1=0
            area=0
            #uart.write(UART_Send(Type, p0, p1, area = area, frame_type=1))

    green_blobs = img.find_blobs([green_threshold],x_stride=5,y_stride=5,pixel_threshold=25,roi=illroi)
    if green_blobs:
        #jiguang()
        look_a=look_a+1
        if(time0%2000<100):
            if(t>800 and look_a>200):
                p_out.high()
        elif(time0%2000>=100):
            p_out.low()
        for blob in green_blobs:
            Type=200
            p0=blob.cx()
            p1=blob.cy()
            area=blob.area()
            #uart.write(UART_Send(Type, p0, p1, area = area, frame_type=1))
            if blob.x()+blob.w()<150:
                img.draw_cross(blob.x()+blob.w(),blob.y())
                Type=202
                p0=blob.w()+blob.x()
                p1=blob.y()
                #uart.write(UART_Send(Type, p0, p1, area = 0, frame_type=1))
    else:
        p_out.off()
    black_blobs = img.find_blobs([black_threshold],x_stride=50,y_stride=3,pixel_threshold=50)
    #judge_right_angle()
    if black_blobs:
        for blob in black_blobs:
            if blob.w()/blob.h() > 5:
                img.draw_rectangle(blob.rect())
                img.draw_cross(blob.cx(), blob.cy())
                Type=201
                p0=blob.rotation_deg()
                p1=blob.cy()
                area=blob.area()
                uart.write(UART_Send(Type, p0, p1, area = area, frame_type=1))
            elif blob.w()/blob.h()>0.5 and blob.w()/blob.h()<1.5 and blob.pixels()>30:
                green_blobs_in_A=img.find_blobs([green_threshold],roi=blob.rect(),x_stride=5,y_stride=5,pixel_threshold=25)
                if green_blobs_in_A:
                    blue_led.on()
                    img.draw_rectangle(blob.rect(),color=(255,0,0))
                    img.draw_cross(blob.cx(), blob.cy(),color=(255,0,0))
                    Type=199
                    p0=blob.cx()
                    p1=blob.cy()
                    area=blob.area()
                    if(t>800):
                        uart.write(UART_Send(Type, p0, p1, area = area, frame_type=1))
                else:
                    blue_led.off()
                    img.draw_rectangle(blob.rect())
                    img.draw_cross(blob.cx(), blob.cy())
                    Type=203
                    p0=blob.cx()
                    p1=blob.cy()
                    area=blob.area()
                    if(t>800):
                        uart.write(UART_Send(Type, p0, p1, area = area, frame_type=1))
