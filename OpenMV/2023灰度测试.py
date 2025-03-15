import sensor, image,time,math
from pyb import Pin, Timer, LED, UART

uart_buf = bytearray([0xAA,0xFF, 0xEE, 0x00,0x00,0x00,0x00, 0x00, 0x00, 0x00])



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
thresholds = [(150, 255)]

class Rect(object):
     x = 0
     y = 0
     flag = 0

Rect=Rect()
def Findblobs(img):
    blobs = img.find_blobs(thresholds, x_stride=10, y_stride=10,area_threshold=10000,  pixels_area=10000)
    filtered_blobs = []
    for blob1 in blobs:
        x, y, width, height = blob1[:4]
        if (width >= 120 and width <= 200) :
            filtered_blobs.append(blob1)
        if len(filtered_blobs) == 0:
             continue
    max_blob = FindMax(filtered_blobs)
    if max_blob:
        img.draw_rectangle(max_blob.rect())
        Rect.x= max_blob.cx()-160
        Rect.y= max_blob.cy()-120
        Rect.flag=max_blob.code()
        print(Rect.x)
        print(Rect.y)
        LED(3).on()
        LED(2).on()
        LED(1).on()
    else:
         Rect.flag = 0
         LED(3).off()
         LED(2).off()
         LED(1).off()

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
clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    img.binary([(150, 255)])
    img.erode(2)
    img.dilate(2)
    img.morph(kernel_size, sharpen_kernel )
    Findblobs(img)

