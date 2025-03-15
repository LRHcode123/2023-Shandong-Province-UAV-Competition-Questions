# 特征点保存例程
# 此示例显示如何将关键点描述符保存到文件。向相机显示一个对象，然后运行
# 该脚本。该脚本将提取并保存关键点描述符和图像。
# 您可以使用keypoints_editor.py 来删除不需要的关键点。
#
# 注意：请在运行此脚本后重置摄像头以查看新文件。
import sensor, time, image

# 重置传感器
sensor.reset()

# 传感器设置
sensor.set_contrast(3)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((320, 240))
sensor.set_pixformat(sensor.GRAYSCALE)

sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False, value=100)

FILE_NAME = "desc"
img = sensor.snapshot()
# 注意：请参阅文档查看其他参数
# 注：默认情况下，find_keypoints返回从图像中提取的多尺度关键点。
kpts = img.find_keypoints(max_keypoints=150, threshold=10, scale_factor=1.2)

if (kpts == None):
    raise(Exception("Couldn't find any keypoints!"))

image.save_descriptor(kpts, "/%s.orb"%(FILE_NAME))
img.save("/%s.pgm"%(FILE_NAME))

img.draw_keypoints(kpts)
sensor.snapshot()
time.sleep_ms(1000)
raise(Exception("Done! Please reset the camera"))

