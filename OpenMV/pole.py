#----pole
import sensor, image,time,math
from pyb import Pin, Timer, LED, UART

uart_buf = bytearray([0xAA,0xFF, 0xFF, 0x00,0x00,0x00,0x00, 0x00, 0x00, 0x00])

#串口三配置
uart = UART(3,500000)
uart.init(500000, bits=8, parity=None, stop=1)
def uartsend(timer):
    uart.write(uart_buf)
    print(uart_buf)
tim = Timer(2, freq=20)
tim.callback(uartsend)


led1 = LED(1)
led2 = LED(2)
led3 = LED(3)
led1.off()
led2.off()
led3.off()

IMG_WIDTH = 320
IMG_HEIGHT = 240

class Pole(object):
    flag=0
    cx=0
    cy=0
    dx=0
    dy=0
    angle=0
    distance=0

poleData=Pole()

IMG_CENTER_X=int(IMG_WIDTH/2)
IMG_CENTER_Y=int(IMG_HEIGHT/2)

black_threshold=(0, 23, -19, 16, -19, 14)#(18, 47, -31, 3, -42, -16)

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

def find_color_pole(img):
    poleData.flag=0
    pixels_max=0
    #直接找色块  找出像素最多的
    for b in img.find_blobs([black_threshold], x_stride=5, y_stride=5,area_threshold=5000):
        if pixels_max<b.pixels() and b.w()<47 and b.w()>5 and b.w()*1.5<b.h():
            img.draw_rectangle(b[0:4])#圈出搜索到的目标
            poleData.flag = 1
            pixels_max=b.pixels()
            poleData.cx = b.cx()
            poleData.cy = b.cy()
            poleData.dx = b.cx()-160
            poleData.dy = b.cy()-120
            img.draw_cross(poleData.cx,poleData.cy, color=127, size = 10)


#中心坐标160 120 中心边界100 220  dx +-60
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
    img = sensor.snapshot().lens_corr(1.8)#拍一张图像
    find_color_pole(img)
    print(clock.fps())
    uart_buf = bytearray([0xAA,0xFF, 0xFF,0x00, poleData.flag ,poleData.dx>>8 ,poleData.dx,
                          (-poleData.dy)>>8 ,(-poleData.dy),0x00,0x00])
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
