import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import time
import keyboard
import threading
import pyautogui

# 定义RGB颜色范围
color_ranges = {
    '长': ([94, 0, 204], [94, 0, 204], 0.67),
    '中长': ([142, 66, 252], [142, 66, 252], 0.57),
    '中短': ([192, 87, 255], [192, 87, 255], 0.39),
    '短': ([231, 131, 255], [231, 131, 255], 0.3)
}

# 根据窗口标题获取窗口坐标
def get_window_coords_by_title(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        x1, y1, x2, y2 = rect
        return x1, y1, x2, y2
    else:
        return None

# 捕获屏幕区域
def screen_capture(x1, y1, x2, y2):
    screen = np.array(ImageGrab.grab(bbox=(x1, y1, x2, y2)))
    return screen

# 检测特定颜色的砖块
def detect_color(image, color_range):
    # 创建颜色掩码
    lower, upper = [np.array(color, dtype="uint8") for color in color_range]
    mask = cv2.inRange(image, lower, upper)
    # 检测颜色
    return cv2.countNonZero(mask) > 0

def perform_jump(delay):
    time.sleep(delay)  # 延时对应时长
    keyboard.press_and_release('space')  # 模拟按空格键进行跳跃
# 窗口标题
window_title = "KOOK"
coords = get_window_coords_by_title(window_title)

if coords:
    print("Window Coordinates:", coords)
    x1, y1, x2, y2 = coords

    # 创建窗口
    cv2.namedWindow('Window', cv2.WINDOW_NORMAL)
    last_block_time = time.time()  # 初始化最后一个砖块检测时间
    # 主循环
    while True:
        screen = screen_capture(x1, y1, x2, y2)
        
        # 只检测屏幕右侧区域
        right_side_width = int(screen.shape[1] * 0.075)  # 可以调整这个百分比以优化检测区域
        right_side = screen[:, -right_side_width:]

        for color_name, (lower, upper, delay) in color_ranges.items():
            if detect_color(right_side, (lower, upper)):
                last_block_time = time.time()  # 更新最后一个砖块检测时间
                print(f"检测到{color_name}砖块，{delay}秒后跳跃！")
                jump_thread = threading.Thread(target=perform_jump, args=(delay,))
                jump_thread.start()  # 在新线程中执行跳跃动作
                time.sleep(1.9)  # 在检测到一个砖块后等待2.5秒再检测下一个砖块
                print(f"开始下一轮检测")
            elif time.time() - last_block_time > 5:
                print("No new block detected in the last 5 seconds. Game over. Clicking to restart.")
                pyautogui.click()  # 模拟鼠标点击以重新开始游戏
                time.sleep(0.5)
                pyautogui.click()  # 获取游戏焦点
                last_block_time = time.time()  # 重置最后一个砖块检测时间
                break

        # 显示处理后的屏幕（调试用）
        cv2.imshow('Window', right_side)
        if cv2.waitKey(25) & 0xFF == ord('q'): # 在处理后的屏幕上按下Q退出
            break

    # 关闭窗口
    cv2.destroyAllWindows()
else:
    print("未找到窗口。")
