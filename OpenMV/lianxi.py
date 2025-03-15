# Untitled - By: Liu - 周三 3月 22 2023

import sensor, image, time, pyb


sensor.reset()#初始化感光元件
sensor.set_pixformat(sensor.GRAYSCALE)#设置为黑白
sensor.set_framesize(sensor.QVGA)#设置图像的大小
sensor.skip_frames(time = 2000)#跳过n张照片，在更改设置后，跳过一些帧，等待感光元件变稳定。
#sensor.set_auto_gain(False) # 关闭自动自动增益。默认开启的。
#sensor.set_auto_whitebal(False) #关闭白平衡。在颜色识别中，一定要关闭白平衡。
clock = time.clock() #创建一个clock便于计算FPS

#将蓝灯赋值给变量led
led = pyb.LED(1) # Red LED = 1, Green LED = 2, Blue LED = 3, IR LEDs = 4.

# 核卷积滤波
kernel_size = 1
kernel = [-2, -1, 0, \
          -1, 1, 1, \
          0, 1, 2]

harpen_kernel = ( 0, -1, 0, \
                 -1,  5,-1, \
                  0, -1, 0)

identity_kernel = (0, 0, 0, \
                   0, 1, 0, \
                   0, 0, 0)

while (True):
    clock.tick()
    img = sensor.snapshot()#拍摄一张照片，img为一个image对
#    histogram = img.get_histogram()
#    Thresholds = histogram.get_threshold()
 #   img.binary([(Thresholds.value(), 255)])
  #  img.erode(2)
    img.morph(kernel_size, identity_kernel)
    print(clock.fps())
