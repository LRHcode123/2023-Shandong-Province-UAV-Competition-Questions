# 利用特征点检测特定物体例程。
# 向相机显示一个对象，然后运行该脚本。 一组关键点将被提取一次，然后
# 在以下帧中进行跟踪。 如果您想要一组新的关键点，请重新运行该脚本。
# 注意：请参阅文档以调整find_keypoints和match_keypoints。
import sensor, time, image

# Reset sensor
sensor.reset()

# Sensor settings
sensor.set_contrast(3)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((320, 240))
sensor.set_pixformat(sensor.GRAYSCALE)

sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False, value=100)

#画出特征点
def draw_keypoints(img, kpts):
    if kpts:
        print(kpts)
        img.draw_keypoints(kpts)
        img = sensor.snapshot()
        time.sleep_ms(1000)
kpts1 = image.load_descriptor("/desc.orb")
clock = time.clock()

while (True):
    clock.tick()
    img = sensor.snapshot()
    kpts2 = img.find_keypoints(max_keypoints=150, threshold=10, normalized=True)
    #如果检测到特征物体
    if (kpts2):
        #匹配当前找到的特征和最初的目标特征的相似度
        match = image.match_descriptor(kpts1, kpts2, threshold=85)
        #image.match_descriptor(descritor0, descriptor1, threshold=70, filter_outliers=False)。本函数返回kptmatch对象。
        #threshold阈值设置匹配的准确度，用来过滤掉有歧义的匹配。这个值越小，准确度越高。阈值范围0～100，默认70
        #filter_outliers默认关闭。

        #match.count()是kpt1和kpt2的匹配的近似特征点数目。
        #如果大于10，证明两个特征相似，匹配成功。
        if (match.count()>10):
            # If we have at least n "good matches"
            # Draw bounding rectangle and cross.
            #在匹配到的目标特征中心画十字和矩形框。
            img.draw_rectangle(match.rect())
            img.draw_cross(match.cx(), match.cy(), size=10)

        #match.theta()是匹配到的特征物体相对目标物体的旋转角度。
        print(kpts2, "matched:%d dt:%d"%(match.count(), match.theta()))
        #不建议draw_keypoints画出特征角点。
        # NOTE: uncomment if you want to draw the keypoints
        #img.draw_keypoints(kpts2, size=KEYPOINTS_SIZE, matched=True)

    # Draw FPS
    #打印帧率。
    img.draw_string(0, 0, "FPS:%.2f"%(clock.fps()))
