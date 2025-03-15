#

import sensor, gif

# Setup camera. 设置摄像机。
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames()

# Create the gif object. 创建一个gif对象。
g = gif.Gif("example.gif")

# Add frames. 添加帧。
for i in range(300):
    g.add_frame(sensor.snapshot())

# Finalize. 完成。
g.close()
