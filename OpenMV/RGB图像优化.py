# RGB图像测试 - By: Liu - 周日 7月 23 2023

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
#sensor.set_gainceiling(2)#设置相机增益 2, 4, 8, 16, 32, 64, 128
#sensor.set_contrast(3) #设置相机图像对比度 -3至+3 画面亮暗变化 -3到+3逐渐变亮
#sensor.set_brightness(3) #设置相机图像亮度 -3至+3
#sensor.set_saturation(+3) #设置相机图像饱和度 -3至+3 黑白变鲜艳
#sensor.set_quality(0) #设置相机图像JPEG压缩质量 0-100
clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot()
    print(clock.fps())
