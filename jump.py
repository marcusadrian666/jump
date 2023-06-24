# 导入所需的模块
import cv2
import numpy as np
import time
import os

# 定义按压时间系数，可以根据具体情况调整
press_coefficient = 1.35

# 定义adb命令的函数，用于执行手机操作
def adb_command(command):
    os.system('adb ' + command)

# 定义截图函数，用于获取手机当前画面
def screenshot():
    adb_command('shell screencap -p /sdcard/autojump.png')
    adb_command('pull /sdcard/autojump.png .')

# 定义找圆心函数，用于寻找小人的位置
def find_circle(image):
    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 使用霍夫变换检测圆形
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100, param1=100, param2=35, minRadius=20, maxRadius=50)
    # 返回圆心坐标
    if circles is not None:
        x, y, r = circles[0][0]
        return int(x), int(y)
    else:
        return None

# 定义找棋盘函数，用于寻找下一个跳跃目标的位置
def find_chessboard(image):
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # 设定白色的阈值范围
    lower_white = np.array([0, 0, 221])
    upper_white = np.array([180, 30, 255])
    # 根据阈值构建掩模
    mask = cv2.inRange(hsv, lower_white, upper_white)
    # 对掩模进行腐蚀和膨胀操作，去除噪点
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)
    # 使用Canny算法检测边缘
    edges = cv2.Canny(mask, 100, 200)
    # 使用霍夫变换检测直线
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
    # 计算所有直线的斜率和截距的平均值，得到棋盘的中线方程
    if lines is not None:
        k_sum = 0
        b_sum = 0
        n = len(lines)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x1 != x2:
                k = (y2 - y1) / (x2 - x1)
                b = y1 - k * x1
                k_sum += k
                b_sum += b
        k_mean = k_sum / n
        b_mean = b_sum / n
        # 计算中线与图片下边缘的交点坐标，作为棋盘的中心位置
        x = int((image.shape[0] - b_mean) / k_mean)
        y = image.shape[0]
        return x, y
    else:
        return None

# 定义主函数，用于循环执行跳跃操作
def main():
    while True:
        # 获取截图
        screenshot()
        image = cv2.imread('autojump.png')
        # 寻找小人位置和棋盘位置
        circle_pos = find_circle(image)
        chessboard_pos = find_chessboard(image)
        # 如果都找到了，计算距离和按压时间
        if circle_pos and chessboard_pos:
            distance = np.sqrt((circle_pos[0] - chessboard_pos[0]) ** 2 + (circle_pos[1] - chessboard_pos[1]) ** 2)
            press_time = int(distance * press_coefficient)
            # 模拟按压屏幕
            adb_command('shell input swipe 300 300 300 300 ' + str(press_time))
            # 等待下一次跳跃
            time.sleep(1.5)
        else:
            # 如果没有找到，结束程序
            print('Game over!')
            break

# 调用主函数
if __name__ == '__main__':
    main()
