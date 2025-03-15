# 机器学习+形状识别
# This code run in OpenMV4 H7

import sensor, image, time, os, tf,math
from pyb import Pin, Timer, LED, UART
uart_buf = bytearray([0xAA,0xFF, 0xEE, 0x00,0x00,0x00,0x00, 0x00, 0x00, 0x00])

#串口三配置
uart = UART(3,500000)
uart.init(500000, bits=8, parity=None, stop=1)
def uartsend(timer):
    uart.write(uart_buf)
    print(uart_buf)
tim = Timer(2, freq=20)
tim.callback(uartsend)
color=(0,255,0)

class C:
    x=0
    y=0
    blobs_flag = 0
    blobs_shape  = 0

c=C()
thresholds = [(30, 46, 15, 70, 12, 53)]#(8, 27, 8, 25, 8, 30)]
def FindMax(blobs):
    if blobs:
        most_pixels = 0
        largest_blob = 0
        for i in range(len(blobs)):
            if blobs[i].pixels() > most_pixels:
                most_pixels = blobs[i].pixels()
                largest_blob = i
                max_blob = blobs[largest_blob]
        return max_blob

def detectrect(max_blob):#输入的是寻找到色块中的最大色块
    row_data=[0,0,0]#保存颜色和形状
   # print(max_blob.solidity())
    if max_blob.solidity()>0.9 or max_blob.density()>0.84:
        row_data[0]=max_blob.code()
        img.draw_rectangle(max_blob.rect())
        row_data[1]='rectangle'#表示矩形
        row_data[2]=1
        c.x= max_blob.cx()-48
        c.y= max_blob.cy()-48
        c.blobs_flag=row_data[0]
        c.blobs_shape =row_data[2]
        LED(3).on()
        LED(2).on()
        LED(1).on()
    else:
         c.blobs_flag = 0
         c.blobs_shape  = 0
         LED(3).off()
         LED(2).off()
         LED(1).off()
    print(row_data)
    return row_data #返回的是两个值，颜色和形状

def detectcir(max_blob):#输入的是寻找到色块中的最大色块
    row_data=[0,0,0]#保存颜色和形状
    if max_blob.density()>0.6:
        img.draw_circle((max_blob.cx(), max_blob.cy(),int((max_blob.w()+max_blob.h())/4)))
        row_data[0]=max_blob.code()
        row_data[1]='circle'#表示圆形
        row_data[2]=2
        c.x= max_blob.cx()-48
        c.y= max_blob.cy()-48
        c.blobs_flag=row_data[0]
        c.blobs_shape =row_data[2]
        LED(3).on()
        LED(2).on()
        LED(1).on()
    else:
         c.blobs_flag = 0
         c.blobs_shape  = 0
         LED(3).off()
         LED(2).off()
         LED(1).off()
    print(row_data)
    return row_data

def detecttri(max_blob):#输入的是寻找到色块中的最大色块
    row_data=[0,0,0]#保存颜色和形状
    if max_blob.density()>0.4:
        img.draw_cross(max_blob.cx(), max_blob.cy())
        row_data[0]=max_blob.code()
        row_data[1]='triangle'#表示三角形
        row_data[2]=3
        c.x= max_blob.cx()-48
        c.y= max_blob.cy()-48
        c.blobs_flag=row_data[0]
        c.blobs_shape =row_data[2]
        LED(3).on()
        LED(2).on()
        LED(1).on()
    else:
         c.blobs_flag = 0
         c.blobs_shape = 0
         LED(3).off()
         LED(2).off()
         LED(1).off()
    print(row_data)
    return row_data #返回的是两个值，颜色和形状


sensor.reset()                         # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)    # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)      # Set frame size to QQVGA (160x120)
sensor.set_windowing((96, 96))       # Set 96x96 window.
sensor.skip_frames(time=2000)          # Let the camera adjust.
sensor.set_hmirror(True)
sensor.set_vflip(True)
labels = [line.rstrip() for line in open("labels.txt")]
class_num = len(labels)

clock = time.clock()
while(True):
    clock.tick()
    img = sensor.snapshot()
    blobs = img.find_blobs(thresholds, x_stride=5, y_stride=5,area_threshold=200)
    max_blob = FindMax(blobs)
    for obj in tf.classify("trained.tflite", img, min_scale=1.0, scale_mul=0.8, x_overlap=0.5, y_overlap=0.5):
        output = obj.output()
        if max_blob:
            if output[0]>0.98:
                row_data=detectrect(max_blob)
            elif output[1]>0.95:
                row_data=detecttri(max_blob)
            elif output[2]>0.90:
                row_data=detectcir(max_blob)
            else:
                 c.blobs_flag = 0
                 c.blobs_shape = 0
                 LED(3).off()
                 LED(2).off()
                 LED(1).off()
        else:
              c.blobs_flag = 0
              c.blobs_shape = 0
              LED(3).off()
              LED(2).off()
              LED(1).off()
    print(clock.fps(), "fps")
    for i in range(class_num):
        print("%s = %f" % (labels[i], output[i]))
    uart_buf = bytearray([0xAA,0xFF, 0xEE, 0x00, c.x>>8,c.x,(-c.y)>>8,(-c.y),c.blobs_flag,c.blobs_shape, 0x00, 0x00])
    lens = len(uart_buf)#数据包大小
    uart_buf[3] = lens-6;#有效数据个数
    i = 0
    sum = 0
    sum1 = 0
    #和校验
    while i<(lens-2):
        sum = sum + uart_buf[i]
        sum1 = sum1 + sum
        i = i+1
    uart_buf[lens-2] = sum;
    uart_buf[lens-1] = sum1;

