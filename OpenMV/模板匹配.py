import time, sensor, image
from image import SEARCH_EX, SEARCH_DS

sensor.reset()
sensor.set_contrast(1)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)

template = image.Image("/4.pgm")

clock = time.clock()

while (True):
    clock.tick()
    img = sensor.snapshot()
    r = img.find_template(template, 0.50, step=4, search=SEARCH_EX) # roi=(10, 0, 60, 60))
    if r:
        img.draw_rectangle(r)
        img.draw_cross(r[0]+(r[2]//2),r[1]+(r[3]//2),size=10)
    print(clock.fps())
