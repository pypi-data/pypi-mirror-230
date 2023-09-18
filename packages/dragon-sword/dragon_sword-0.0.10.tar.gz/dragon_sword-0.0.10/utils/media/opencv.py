import time

import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import pytesseract as tess
from PIL import Image
from mss import mss
from typing import Iterable
import pyautogui
from third_party.wrm.log import logger


def esc_quit():
    """
    按esc，返回True，关闭所有窗口，上层关闭程序
    按c，返回False，关闭所有窗口，上层可继续
    """
    key = cv.waitKey(0)
    if key == 27 or key == 'c':  # 27是ESC键值
        cv.destroyAllWindows()
    return key == 27


def img_height(img):
    return img.shape[0]


def img_width(img):
    return img.shape[1]


def display_img(img):
    plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    plt.show()

    # cv.namedWindow("cv")
    # cv.imshow("cv", img)
    return esc_quit()


def display_img_s(img_s):
    for i in range(len(img_s)):
        cv.namedWindow(f"{i}")
        cv.imshow(f"{i}", img_s[i])
    return esc_quit()


def display_img_by_name(img_path):
    img = cv.imread(img_path)
    display_img(img)


def capture_screen_new():
    size = pyautogui.size()
    mon = {"left": 0, "top": 0, "width": size[0] + 1, "height": size[1] + 1}
    with mss() as sct:
        while True:
            cap = sct.grab(mon)
            img = Image.frombytes("RGB", (cap.width, cap.height), cap.rgb, )
            img = np.array(img)
            img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
            yield img


def capture_screen(img_handler):
    size = pyautogui.size()
    mon = {"left": 0, "top": 0, "width": size[0] + 1, "height": size[1] + 1}
    with mss() as sct:
        while True:
            cap = sct.grab(mon)
            img = Image.frombytes("RGB", (cap.width, cap.height), cap.rgb, )
            img = np.array(img)
            img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
            if_continue = img_handler(img)
            if not if_continue:
                break
            time.sleep(1)


def img_ocr(img) -> str:
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    result = tess.image_to_string(img)
    return result


def extract_image(file_path) -> Iterable:
    # 开始读视频
    video_capture = cv.VideoCapture(file_path)

    while True:
        success, frame = video_capture.read()
        if not success:
            break
        yield frame


def save_img(frame, file_path):
    cv.imwrite(file_path, frame, [int(cv.IMWRITE_PNG_COMPRESSION), 0])


def cut_img(img, left_top=(0, 0), right_top=(0, 0)):
    return img[left_top[1]:right_top[1], left_top[0]:right_top[0], :]


def canny_test(img):
    """
    同构滑动条，测试边缘提取效果
    """
    cv.namedWindow("canny")
    cv.namedWindow("canny2")
    cv.namedWindow("threshold")

    def compute(tmp=0):
        thresh_low = cv.getTrackbarPos("thresh1", "canny")
        thresh_high = cv.getTrackbarPos("thresh2", "canny")
        thresh = cv.getTrackbarPos("thresh", "canny")
        ksize = cv.getTrackbarPos("ksize", "canny")
        sigma = cv.getTrackbarPos("sigma", "canny")
        if ksize % 2 == 0:
            logger.info("gauss error")
            return

        logger.info(f"{thresh_low} {thresh_high} {ksize}")
        # blur_img = cv.medianBlur(img, ksize)
        blur_img = cv.GaussianBlur(img, (ksize, ksize), sigma)

        _, threshold_img = cv.threshold(blur_img, thresh, 255, cv.THRESH_BINARY)
        cv.imshow("threshold", threshold_img)

        edge = cv.Canny(blur_img, thresh_low, thresh_high)
        cv.imshow("canny", edge)

        edge1 = cv.Canny(threshold_img, thresh_low, thresh_high)
        cv.imshow("canny2", edge1)

    thresh1 = 0
    thresh2 = 0
    cv.createTrackbar("thresh1", "canny", thresh1, 255, compute)
    cv.createTrackbar("thresh2", "canny", thresh2, 255, compute)
    cv.createTrackbar("thresh", "canny", thresh2, 255, compute)
    cv.createTrackbar("ksize", "canny", 1, 100, compute)
    cv.createTrackbar("sigma", "canny", 0, 100, compute)
    compute(0)

    esc_quit()


def min_area_rect(img, contour):
    """
    基于图像和边缘点，画外接矩形
    """
    # （（最小外接矩形的中心坐标），（宽，高），旋转角度）
    rect = cv.minAreaRect(contour)
    size = rect[1][0] * rect[1][1]
    if size < 200:
        return
    # 画外接矩形
    box = np.int0(cv.boxPoints(rect))
    cv.drawContours(img, [box], -1, (36, 255, 12), 2)
    logger.debug("cnt size=%s", rect)


def ellipse_contour(img, contour):
    # 椭圆拟合
    # ellipse = [ (x, y) , (a, b), angle ]
    # （x, y）代表椭圆中心点的位置
    # （a, b）代表长短轴长度，应注意a、b为长短轴的直径，而非半径
    # angle 代表了中心旋转的角度
    ellipse = cv.fitEllipse(contour)
    # 计算椭圆面积
    size = 3.14 * ellipse[1][0] * ellipse[1][1] / 4
    angle = ellipse[2]
    if size < 5000 or angle < 85 or angle > 100:
        return None
    cv.ellipse(img, ellipse, 0)
    logger.debug("ellipse size=%s angle=%s", size, ellipse[2])
    return ellipse


def match_template(screen, target) -> (cv.Mat, int, int, bool):
    height, width, channels = target.shape
    res = cv.matchTemplate(screen, target, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    if max_val <= 0.95:
        return screen, 0, 0, False
    logger.debug(f"{min_val} {max_val} {min_loc} {max_loc}")

    x_center, y_center = max_loc[0] + width // 2, max_loc[1] + height // 2
    logger.debug(f"x={x_center} y={y_center}")
    cv.circle(screen, (x_center, y_center), 5, 255, -1)

    tl = max_loc
    br = (tl[0] + width, tl[1] + height)
    cv.rectangle(screen, tl, br, (0, 0, 255), 2)

    if cv.minMaxLoc(res)[1] > 0.95:
        logger.info("find")
    return screen, x_center, y_center, True
