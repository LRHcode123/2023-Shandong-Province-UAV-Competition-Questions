#RGB拆分为三通道
import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

while True:
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    statistics = img.get_statistics() # 像素颜色统计
    print(statistics)

    # 获取Lab颜色通道的众数
    l_mode = statistics.l_mode()
    a_mode = statistics.a_mode()
    b_mode = statistics.b_mode()

    # 对Lab通道的众数进行限制（根据实际情况进行调整）
    if 0 < l_mode < 100 and 0 < a_mode < 127 and 0 < b_mode < 127:
        # 识别到红色色块
        blobs = img.find_blobs([(l_mode, a_mode, b_mode)], pixels_threshold=100, area_threshold=100)
        if blobs:
            for blob in blobs:
                img.draw_circle(blob.cx(), blob.cy(), blob.r(), color=(255, 0, 0)) # 用红色圆框标记红色圆形区域

    else:
        # 未识别到红色色块，用白色矩形标记
        img.draw_rectangle(0, 0, img.width(), img.height(), color=(255, 255, 255))

    print("FPS %f" % clock.fps())
