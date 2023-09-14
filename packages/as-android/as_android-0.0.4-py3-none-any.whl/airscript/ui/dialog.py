from typing import Any

from airscript.ui import Window


def toast(msg: str, duration: int = 3, x=-1, y=-1) -> None:
    pass


def alert(msg: str, submit: str) -> None:
    pass


class confirm:
    def __init__(self, msg: str):
        pass

    def title(self, msg: str) -> 'confirm':
        pass

    def submit(self, msg: str) -> 'confirm':
        pass

    def cancel(self, msg: str) -> 'confirm':
        pass

    def close(self):
        pass

    def show(self, pyfun: Any):
        pass


class promat:
    def __init__(self, msg: str):
        pass

    def title(self, msg: str) -> 'promat':
        pass

    def value(self, msg: str) -> 'promat':
        pass

    def hint(self, msg: str) -> 'promat':
        pass

    def submit(self, msg: str) -> 'promat':
        pass

    def cancel(self, msg: str) -> 'promat':
        pass

    def close(self):
        pass

    def show(self, pyfun: Any = None):
        pass


class loger(Window):
    def __init__(self, tuner: Any = None, layout: str = None):
        """
        loger 继承自Window

        @param tuner: 消息通道
        @param layout: 自定义布局(注意该 布局必须包含给定模版中的 js方法.)
        """
        super().__init__(layout)

    def show(self, pyfun: Any = None):
        pass
