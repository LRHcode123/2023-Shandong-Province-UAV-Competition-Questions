# Untitled - By: Liu - 周四 7月 27 2023

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    for l in img.find_lines(threshold=2500,theta_margin = 50, rho_margin = 50):
        img.draw_line(l.line(),color=(0,0,255))
    print(clock.fps())
