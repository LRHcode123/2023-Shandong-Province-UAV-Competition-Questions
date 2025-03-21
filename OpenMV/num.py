import sensor, image, time, os, tf
from pyb import LED
sensor.reset()                         # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE)    # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)      # Set frame size to QVGA (320x240)
sensor.set_windowing((240, 240))       # Set 240x240 window.
sensor.skip_frames(time=2000)          # Let the camera adjust.
sensor.set_auto_gain(False) # 关闭自动自动增益。默认开启的。
sensor.set_auto_whitebal(False) #关闭白平衡。在颜色识别中，一定要关闭白平衡。
clock = time.clock()
led=LED(1)
#led.on()
while(True):
    clock.tick()
    img = sensor.snapshot().binary([(141,255)])
    #for obj in tf.classify("trained.tflite", img, min_scale=1.0, scale_mul=0.5, x_overlap=0.0, y_overlap=0.0):
        #print(obj.output())
    print(clock.fps(), "fps")
