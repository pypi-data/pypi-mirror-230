from typing import Union

from airscript import graphics


# 点击
def click(x: Union[int, graphics.Point], y=None, dur=20) -> None:
    """
    点击屏幕某个位置
    可传入一组坐标，也可以传入 一个Point对象
    """
    if isinstance(x, graphics.Point):
        point = x
        x = point.x
        y = point.y
    elif y is None:
        raise ValueError("If the first argument is not a Point, both x and y should be provided.")


# 滑动
def slide(x: int, y: int, y1: int, dur=20) -> None:
    pass


# 输入
def input(data: str) -> None:
    pass


#捕获动作
class Catch:
    def click(self):
        return self

    def msg(self, message: str):
        return self

    def shine(self, isShine: bool):
        return self
