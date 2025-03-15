#By: Liu - 周五 7月 21 2023

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)#拍一张图像
    for c in img.find_circles(threshold = 2200, x_margin = 10, y_margin = 5, r_margin = 5,r_min = 2, r_max = 100, r_step = 2):
        img.draw_circle(c.x(),c.y(),c.r(), color = (0, 0, 255))
        #cx = c.x()-c.r()
        #cx1 = c.x()
        #cy = c.y()-c.r()
        #cy1 = c.y()
        #cr = 2*c.r()
        #roi1 = (cx,cy,cr,cr)
        #blobs1 = img.find_blobs(black, roi=roi1, x_stride=5, y_stride=5,area_threshold=20)
        #max_blob1 = FindMax(blobs1)
        #if max_blob1:
            #img.draw_cross(max_blob1.cx(), max_blob1.cy())#物体中心画十字
            #img.draw_rectangle(max_blob1.rect())#画圈
            ##获取坐标并转换为+-200
            #x = max_blob1.cx()-80
            #y = max_blob1.cy()-60
            #blobs_flag = 4
            #LED(3).toggle()
            #LED(2).toggle()
        #else:
            #blobs_flag = 0
            #LED(2).off()
            #LED(3).off()
    print(clock.fps())
