import sensor, image,time,math
from pyb import Pin, Timer, LED, UART

uart_buf1 = bytearray([0xAA,0xFF, 0xCC, 0x00,0x00,0x00,0x00, 0x00])

#串口三配置
uart = UART(3,500000)
uart.init(500000, bits=8, parity=None, stop=1)

def uartsend(timer):
    uart.write(uart_buf1)
    print(uart_buf1)
tim = Timer(2, freq=20)
tim.callback(uartsend)
#色块识别函数
#定义函数：找到画面中最大的指定色块
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
black = (0,0)
threshold = (0,0)
red=[66,66,66]
# 核卷积滤波

black_threshold=(231, 255)
black_threshold1=(200, 255)
kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.

kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]

sharpen_kernel = ( 0, -1, 0, \
                  -1,  5,-1, \
                   0, -1, 0)

identity_kernel = (0, 0, 0, \
                   0, 1, 0, \
                   0, 0, 0)
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_hmirror(True)
sensor.set_vflip(True)
clock = time.clock()
while(True):
     clock.tick()
     img = sensor.snapshot().lens_corr(1.8)
     img.binary([(0, 95)])
     #img.erode(2)
     img.dilate(2)
     img.morph(kernel_size, sharpen_kernel )
     blobs = img.find_blobs([black_threshold], x_stride=5, y_stride=5,area_threshold=10)
     max_blob = FindMax(blobs)
     if max_blob:
         img.draw_cross(max_blob.cx(), max_blob.cy(),color=red)#物体中心画十字
         img.draw_rectangle(max_blob.rect())#画圈
         #获取坐标并转换为+-200
         x1 = max_blob.cx()-80
         y1 = max_blob.cy()-60
         x2 = 80-max_blob.x()
         y2 = 60-max_blob.y()
         #print(x1,y1)
         print("x2:",x2,"y2:",y2)
         #LED灯闪烁
         LED(3).toggle()
         #LED灯闪烁
         LED(2).toggle()
     else:
         x2=0
         y2=0
         LED(2).off()
         LED(3).off()
     uart_buf1 = bytearray([0xAA,0xFF, 0xDD, 0x00, x2, y2, 0x00, 0x00])
     lens = len(uart_buf1)#数据包大小
     uart_buf1[3] = lens-6;#有效数据个数
     i = 0
     sum = 0
     sum1 = 0
     #和校验
     while i<(lens-2):
         sum = sum + uart_buf1[i]
         sum1 = sum1 + sum
         i = i+1
     uart_buf1[lens-2] = sum;
     uart_buf1[lens-1] = sum1;
     print(clock.fps(), "fps")


