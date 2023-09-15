"""
@Author: kang.yang
@Date: 2023/9/14 14:43
"""
import subprocess
import time

import pyautogui

from kuto.utils.common import screenshot_util
from kuto.utils.log import logger


class MacDriver(object):

    def __init__(self, pkg_name: str = None):
        self.app_name = pkg_name

    def get_location(self):
        """获取鼠标位置坐标"""
        while True:
            time.sleep(3)
            x, y = pyautogui.position()
            print(x, y)

    def start_app(self):
        if self.app_name is None:
            raise KeyError("应用名不能为空")

        logger.info(f'启动应用: {self.app_name}')
        cmd = f"open -a '{self.app_name}'"
        subprocess.Popen(cmd, shell=True)

    def stop_app(self):
        if self.app_name is None:
            raise KeyError("应用名不能为空")

        logger.info(f'关闭应用: {self.app_name}')
        cmd = f"killall '{self.app_name}'"
        subprocess.Popen(cmd, shell=True)

    def locate(self, image_path: str):
        """根据图片获取坐标"""
        try:
            x, y = pyautogui.locateCenterOnScreen(image_path)
            return x / 2, y / 2
        except:
            return None

    def is_on_screen(self, x, y):
        """坐标是否在屏幕中"""
        return pyautogui.onScreen(x, y)

    def click(self, x, y):
        logger.info(f"点击: ({x}, {y})")
        pyautogui.click(x, y)

    def input(self, text: str):
        logger.info(f"输入: {text}")
        pyautogui.write(text)

    def enter(self):
        logger.info("回车")
        pyautogui.press("enter")

    def screenshot(self, file_name=None, position: str = None):
        return screenshot_util(pyautogui, file_name=file_name, position=position)


if __name__ == '__main__':
    MacDriver(pkg_name='111').get_location()



