from airscript.graphics import Point


def home():
    """
    Press the Home key.
    """
    pass


def back():
    """
    Press the Back key.
    """
    pass


def notifactions():
    """
    Open the notification shade.
    """
    pass


def lockscreen():
    """
    Turn the screen off and show the lock screen immediately.
    """
    pass


def screenshot():
    """
    Take a screenshot.
    """
    pass


def recents():
    """
    Open the recent apps view.
    """
    pass


class Catch:
    def __init__(self):
        pass

    def click(self) -> Point:
        """
        捕捉用户点击坐标

        返回结果:
        - Point: 点位对象，可通过 .x 和 .y 获取坐标
        """
        pass

    def msg(self, text: str) -> 'Catch':
        """
        设置捕获界面展示的信息

        参数:
        - text (str): 展示的文本信息

        返回结果:
        - Catch: Catch对象，用于链式调用其他方法
        """
        pass

    def shine(self, isShine: bool) -> 'Catch':
        """
        设置捕获界面是否闪屏

        参数:
        - isShine (bool): True表示闪屏，False表示不闪屏

        返回结果:
        - Catch: Catch对象，用于链式调用其他方法
        """
        pass


