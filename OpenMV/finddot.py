import sensor,time,pyb,math,sys,image
from pyb import Pin, Timer, LED, UART
from image import SEARCH_EX, SEARCH_DS
sensor.reset()
sensor.set_pixformat(sensor.RGB565) # 灰度更快RGB565
sensor.set_framesize(sensor.QQVGA)#-2Q
sensor.set_hmirror(True)
sensor.set_vflip(True)
sensor.skip_frames(time = 2000)

sensor.set_contrast(1)
sensor.set_gainceiling(16)
# Max resolution for template matching with SEARCH_EX is QQVGA

clock = time.clock()
black =(0, 23, -34, 32, -8, 14)   #(44, 255)

ROI=(45,20,70,100)

templates = ["/A1.pgm","/A2.pgm","/A3.pgm","/A4.pgm","/A5.pgm"]
led = pyb.LED(3)

#xy平面误差数据
err_x = 0
err_y = 0

#发送数据
uart_buf1 = bytearray([0xAA,0xFF, 0xAA, 0x00, 0xFF, 0x00,0x00,0x00,0x00, 0x00, 0x00, 0x00, 0x00])

#串口三配置
uart = UART(3,500000)
uart.init(500000, bits=8, parity=None, stop=1)

def uartsend(timer):
    uart.write(uart_buf1)
    print(uart_buf1)
tim = Timer(2, freq=20)
tim.callback(uartsend)

atan = 0
atan_A = 0
while(True):
    clock.tick()
    img = sensor.snapshot()
    STA = 0x00
    STA2 = 0x00
    cx1 = 0
    cy1 = 0
    fx = 80
    fy = 60
    led.on()            #亮灯
    for c in img.find_rects(threshold = 4500):
        img.draw_rect(c.x(),c.y(),c.w(),c.h(), color = (0, 0, 0))
        cx = c.x()-c.r()
        cx1 = c.x()
        cy = c.y()-c.r()
        cy1 = c.y()
        cr = 2*c.r()
        #cr1 = c.r()
        roi1 = (c.x(),c.y(),c.w(),c.h())
        blobs = img.find_blobs([black], roi=roi1, x_stride=5, y_stride=5,area_threshold=20)
        if blobs:
            most_pixels = 0
            largest_blob = 0
            STA = 0xFF#跟随
            #print("cir",cx1,cy1)
            for i in range(len(blobs)):
                if blobs[i].pixels() > most_pixels:
                    most_pixels = blobs[i].pixels()
                    largest_blob = i
                    #y = int(blobs[largest_blob].cy())
                    #x = int(blobs[largest_blob].cx())
                    #led1.on()
            img.draw_cross(blobs[largest_blob].cx(),blobs[largest_blob].cy())
            img.draw_rectangle(blobs[largest_blob].rect())
        else:
            STA = 0x00
            cx1 = 80
            cy1 = 60
        if STA == 0xFF:
            atan = int((180/3.1416)*(math.atan2(abs(fx-cx1),abs(fy-cy1))))
            print(atan)

    blobss = img.find_blobs([black],roi=ROI,area_pixels = 200)
    if blobss:
        most_pixelss = 0
        largest_blobs = 0
        for i in range(len(blobss)):
            #目标区域找到的颜色块可能不止一个，找到最大的一个
            if blobss[i].pixels() > most_pixelss:
                most_pixelss = blobss[i].pixels()
                largest_blobs = i
                #位置环用到的变量
                err_y = int(blobss[largest_blobs].cy())
                err_x = int(blobss[largest_blobs].cx())
                STA2 = 0XFF
                atan_A = int(180/3.14159*math.atan2(abs(80-err_x),abs(60-err_y)))

        img.draw_cross(blobss[largest_blobs].cx(),blobss[largest_blobs].cy())#调试使用
        img.draw_rectangle(blobss[largest_blobs].rect())
    else:
        err_x = 80
        err_y = 60
        STA2 = 0X00
        atan_A = 6

    uart_buf1 = bytearray([0xAA,0xFF, 0xCC, 0x00, STA, STA2, atan, cx1,cy1,err_x,err_y, atan_A,0x00, 0x00])
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

