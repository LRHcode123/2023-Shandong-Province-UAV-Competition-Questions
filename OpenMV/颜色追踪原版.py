# 单颜色组合识别例程
#
# 这个例子显示了使用OpenMV的单色代码跟踪。
#
#颜色代码是由两种或更多颜色组成的色块。下面的例子只会跟踪同时具有以下两种颜色的彩色物体。

import sensor, image, time

# 颜色跟踪阈值(L Min, L Max, A Min, A Max, B Min, B Max)
# 下面的阈值一般跟踪红色/绿色的东西。你可以调整它们…
thresholds = [ # generic_red_thresholds -> index is 0 so code == (1 << 0)
              (14, 30, -11, 3, -10, 16)] # generic_green_thresholds -> index is 1 so code == (1 << 1)
# 当“find_blobs”的“merge = True”时，code代码被组合在一起。

sensor.reset()
#初始化摄像头，reset()是sensor模块里面的函数

sensor.set_pixformat(sensor.RGB565)
#设置图像色彩格式，有RGB565色彩图和GRAYSCALE灰度图两种

sensor.set_framesize(sensor.QVGA)
#设置图像像素大小

sensor.skip_frames(time = 2000)

clock = time.clock()

# 只有比“pixel_threshold”多的像素和多于“area_threshold”的区域才被
# 下面的“find_blobs”返回。 如果更改相机分辨率，
# 请更改“pixels_threshold”和“area_threshold”。 “merge = True”合并图像中所有重叠的色块。


while(True):
    clock.tick()
    img = sensor.snapshot()
    for blob in img.find_blobs(thresholds, pixels_threshold=100, area_threshold=100):
        if blob.code() == 1: # r/g code == (1 << 1) | (1 << 0)
            # These values depend on the blob not being circular - otherwise they will be shaky.
            img.draw_edges(blob.min_corners(), color=(255,0,0))
            img.draw_line(blob.major_axis_line(), color=(0,255,0))
            img.draw_line(blob.minor_axis_line(), color=(0,0,255))
            # 这些值始终是稳定的。
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            # 注意-色块的旋转rotation是0-180内的唯一。
    print(clock.fps())
