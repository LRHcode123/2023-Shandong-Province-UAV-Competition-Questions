import sensor, image,time,math
from pyb import Pin, Timer, LED, UART

uart_buf1 = bytearray([0xAA,0xFF, 0xCC, 0x00,0x00,0x00,0x00, 0x00])

#串口三配置
uart = UART(3,500000)
uart.init(500000, bits=8, parity=None, stop=1)

def uartsend(timer):
    uart.write(uart_buf1)
    #print(uart_buf1)
tim = Timer(2, freq=20)
tim.callback(uartsend)
#色块识别函数
#定义函数：找到画面中最大的指定色块
def FindMax(blobs):
    max_size=1
    if blobs:
        max_blob = 0
        for blob in blobs:
            blob_size = blob.w()*blob.h()
            if ( (blob_size > max_size) & (blob_size > 10)   ) :#& (blob.density()<1.2*math.pi/4) & (blob.density()>0.8*math.pi/4)
                if ( math.fabs( blob.w() / blob.h() - 1 ) > 0.4 ) :#if ( math.fabs( blob.w() / blob.h() - 1 ) < 2.0 ) :
                    max_blob=blob
                    max_size = blob.w()*blob.h()
        return max_blob
        #roi1 = (cx,cy,cr,cr)
        #blobs = img.find_blobs([black], roi=roi1, x_stride=5, y_stride=5,area_threshold=20)
        #if blobs:
            #most_pixels = 0
            #largest_blob = 0
            #STA = 0xFF#跟随
            ##print("cir",cx1,cy1)
            #for i in range(len(blobs)):
                #if blobs[i].pixels() > most_pixels:
                    #most_pixels = blobs[i].pixels()
                    #largest_blob = i
                    ##y = int(blobs[largest_blob].cy())
                    ##x = int(blobs[largest_blob].cx())
                    ##led1.on()
            #img.draw_cross(blobs[largest_blob].cx(),blobs[largest_blob].cy())
            #img.draw_rectangle(blobs[largest_blob].rect())
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
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()
while(True):
     clock.tick()
     img = sensor.snapshot().lens_corr(1.8)
     img.binary([(0,50)])
     #img.erode(2)
     img.dilate(2)
     img.morph(kernel_size, sharpen_kernel )
     blobs = img.find_blobs([black_threshold1], x_stride=5, y_stride=5,area_threshold=10)
     max_blob=FindMax(blobs)#找到最大的那个
     if max_blob:
         img.draw_cross(max_blob.cx(), max_blob.cy(),color=red)#物体中心画十字
         img.draw_rectangle(max_blob.rect())#画圈
         #获取坐标并转换为+-200
         x1 = max_blob.cx()-80
         y1 = max_blob.cy()-60
         x2 = max_blob.x()
         y2 = max_blob.y()
         w2 = max_blob.w()
         h2 = max_blob.h()
         #print(x1,y1)
         print("x2:",x2,"y2:",y2)
         print("w2:",w2,"h2:",y2)
         #LED灯闪烁
         LED(3).toggle()
         #LED灯闪烁
         LED(2).toggle()
     else:
         x2=0
         y2=0
         LED(2).off()
         LED(3).off()
         #blobs[largest_blob].x()
         #blobs[largest_blob].y()
     #img.erode(1)
     #img.morph(kernel_size, sharpen_kernel )
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

