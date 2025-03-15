# 一维码和二维码识别 - By: Liu - 周三 7月 19 2023

import sensor, image, time

class Ctrl(object):
    WorkMode = 1    #工作模式
    IsDebug = 1     #不为调试状态时关闭某些图形显示等，有利于提高运行速度
    T_ms = 0
#类的实例化
Ctr=Ctrl()

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot()
    if Ctr.WorkMode == 0 :
        for code in img.find_qrcodes():#二维码识别
            print(code)
    elif Ctr.WorkMode == 1 :
        sensor.set_framesize(sensor.VGA)
        sensor.set_windowing((640, 240))
        for code in img.find_barcodes():
            print(code)
    elif Ctr.WorkMode == 2 :
        for i in range(5):
            img.save("{}.jpg".format(i))
    print(clock.fps())

