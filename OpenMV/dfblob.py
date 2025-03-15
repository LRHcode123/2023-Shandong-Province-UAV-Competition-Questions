# Untitled - By: Liu - 周五 7月 14 2023

import sensor, image, time
from pyb import Pin, Timer, LED, UART
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)


clock = time.clock()



while(1):
    sensor.set_pixformat(sensor.GRAYSCALE)
    clock.tick()
    img = sensor.snapshot()
    print(clock.fps())
    LED(3).off()
