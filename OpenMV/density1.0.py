import sensor, image,time,math
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
def newdetect(max_blob):#输入的是寻找到色块中的最大色块
    row_data=[0,0,0]#保存颜色和形状
   # print(max_blob.solidity())

    if max_blob.solidity()>0.9 or max_blob.density()>0.84:
        row_data[0]=max_blob.code()
        img.draw_rectangle(max_blob.rect())
        row_data[1]='rectangle'#表示矩形
        row_data[2]=1
    elif max_blob.density()>0.6:
        img.draw_circle((max_blob.cx(), max_blob.cy(),int((max_blob.w()+max_blob.h())/4)))
        row_data[0]=max_blob.code()
        row_data[1]='circle'#表示圆形
        row_data[2]=2
    elif max_blob.density()>0.4:
        img.draw_cross(max_blob.cx(), max_blob.cy())
        row_data[0]=max_blob.code()
        row_data[1]='triangle'#表示三角形
        row_data[2]=3
    return row_data #返回的是两个值，颜色和形状

def detect(max_blob):#输入的是寻找到色块中的最大色块
    row_data=[-1,-1]#保存颜色和形状
    print(max_blob.solidity())

    if max_blob.density()>0.84:
        row_data[0]=max_blob.code()
        img.draw_rectangle(max_blob.rect())
        row_data[1]=1#表示矩形
    elif max_blob.density()>0.6:
        img.draw_circle((max_blob.cx(), max_blob.cy(),int((max_blob.w()+max_blob.h())/4)))
        row_data[0]=max_blob.code()
        row_data[1]=2#表示圆形
    elif max_blob.density()>0.4:
        row_data[0]=max_blob.code()
        row_data[1]=3#表示三角形
    return row_data#返回的是两个值，颜色和形状

thresholds = [(22, 44, 27, 69, 0, 46),
              (0, 42, -7, 27, -36, 0),
               (17, 38, 5, 70, -26, 48)
              ]#(30, 46, 15, 70, 12, 53)



x=0
y=0
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
#sensor.set_auto_gain(False) # must be turned off for color tracking
#sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_hmirror(True)
sensor.set_vflip(True)
clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    blobs = img.find_blobs(thresholds, x_stride=5, y_stride=5,area_threshold=100)
    max_blob = FindMax(blobs)
    if max_blob:
        row_data=newdetect(max_blob)
        print(row_data)
        print(clock.fps())
        x= max_blob.cx()-160
        y= max_blob.cy()-120
        blobs_flag=row_data[0]
        blobs_shape=row_data[2]
        LED(3).on()
        LED(2).on()
        LED(1).on()
        #LED(2).toggle()
    else:
         blobs_flag = 0
         blobs_shape = 0
         #LED(2).off()
         LED(3).off()
         LED(2).off()
         LED(1).off()
    uart_buf = bytearray([0xAA,0xFF, 0xEE, 0x00, x>>8,x,(-y)>>8,(-y),blobs_flag,blobs_shape, 0x00, 0x00])
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

