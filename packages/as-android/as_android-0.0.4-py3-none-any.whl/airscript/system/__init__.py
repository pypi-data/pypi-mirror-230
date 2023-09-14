import abc
from typing import Any


class R:
    def __init__(self, path: str) -> None:
        pass

    def sd(self, childpath: str = None) -> str:
        pass

    def context(self):
        """
        获取 android 工程上下文
        """
        pass

    def root(self, childpath: str= None) -> str:
        pass

    def res(self, childpath: str = None) -> str:
        pass

    def ui(self, file: str = None) -> str:
        pass

    def exit(self) -> str:
        pass

    def reboot(self) -> str:
        pass


class Device:

    def id(self) -> 'str':
        pass

    def display(self) -> Any:
        pass

    def name(self) -> str:
        pass

    def brand(self) -> str:
        pass

    def model(self) -> str:
        pass

    def sdk(self) -> str:
        pass

    def version(self) -> str:
        pass

    def ip(self) -> str:
        pass

    def currentAppInfo(self) -> Any:
        pass


class MediaPlayListener(metaclass=abc.ABCMeta):
    def prepare(self, player: Any):
        """
        当音频准备完成后回掉该方法

        调用 player.start() 可播放音频
        调用 player.getDuration() 可获取音频的长度
        """
        pass

    def completion(self):
        """
        音频播放完毕后回调该方法
        """
        pass


class Media:
    @staticmethod
    def volume(percent: int, ptype: int):
        """
        调节音量大小

        :param percent: 音量大小 1-100之间
        :param ptype: 音量类型,默认3; 3 = 音乐回放即媒体音量;5 = 窗口顶部状态栏Notification;4= 警告; 2= 铃声;1 = 系统; 0 =通话
        """
        pass

    @staticmethod
    def talk(text: str):
        """
        语音朗读

        :param text: 要朗读的文字
        """
        pass

    @staticmethod
    def play(path: str, listener: MediaPlayListener):
        """
        播放音频文件
        """
        pass

    @staticmethod
    def recode(path: str, time: int = None):
        """
        录制音频文件
        """
        pass

    @staticmethod
    def vibrate(time: int):
        """
        设备震动
        """
        pass


class Clipboard:
    @staticmethod
    def put(msg: str):
        """
        将数据放入剪贴板
        """
        pass

    @staticmethod
    def get():
        """
        读取剪贴板数据
        """
        pass


class Channel:
    def __init__(self, listener: Any):
        pass
