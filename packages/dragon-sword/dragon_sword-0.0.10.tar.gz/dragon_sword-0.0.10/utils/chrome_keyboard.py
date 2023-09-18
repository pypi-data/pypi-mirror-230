import time

import pyautogui

"""
参考文档：
键盘鼠标文档：https://www.jianshu.com/p/e4f4ca3f6b52
chrome快捷键：https://support.google.com/chrome/answer/10483214?hl=zh-Hans
"""


class _Chrome(object):
    def wait_page(self, num=2):
        # TODO: judge page loaded
        time.sleep(num)

    def close_page(self):
        pyautogui.hotkey('ctrl', 'w')

    # def back_page(self):
    #     pyautogui.hotkey('altleft', 'left')

    def refresh_page(self):
        pyautogui.hotkey('ctrl', 'r')
        self.wait_page()

    def pre_page(self):
        pyautogui.hotkey('ctrl', 'shiftleft', 'tab')

    def next_page(self):
        pyautogui.hotkey('ctrl', 'tab')

    def new_page(self):
        pyautogui.hotkey('ctrl', 't')


Chrome = _Chrome()
