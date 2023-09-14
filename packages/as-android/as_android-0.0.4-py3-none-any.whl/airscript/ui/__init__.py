from typing import Any, Union


class Window:
    def __init__(self, layout: str, tunnel: Any = None):
        pass

    def model(self, model: int):
        pass

    def width(self, size: Union[int, str]):
        pass

    def height(self, size: Union[int, str]):
        pass

    def background(self, bgcolor: str):
        pass

    def drag(self, isDrag: bool):
        pass

    def dimAmount(self, dim: float):
        """
        数值在 0-1之间
        0 :完全没有遮罩,1:完全黑的遮罩,0.5:半透明遮罩,默认为0.5
        """
        pass

    def gravity(self, g: int):
        """
        居中位置（引力） 该方法会影响 x，y 函数 的相对位置
        """
        pass

    def x(self, x: int):
        pass

    def y(self, y: int):
        pass

    def show(self):
        pass

    def close(self):
        pass

    def call(self, func: Any):
        pass

    def tunner(self, func: Any):
        pass


class Float:
    def hide(self):
        pass

    def show(self):
        pass



