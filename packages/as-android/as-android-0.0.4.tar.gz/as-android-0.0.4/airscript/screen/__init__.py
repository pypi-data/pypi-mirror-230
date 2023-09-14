from typing import Any
from typing import List, Optional, Tuple

from airscript.graphics import Point
from airscript.system import R


class Bitmap:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.pixels: List[List[Tuple[int, int, int]]] = [[(0, 0, 0)] * width for _ in range(height)]

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        self.pixels[y][x] = color

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
        return self.pixels[y][x]

    # 其他方法和属性的类型注释
    # ...


class Screen:
    @staticmethod
    def bitmap(x: int = None, y: int = None, x1: int = None, y1: int = None) -> Bitmap:
        """
        将屏幕指定区域截取为Bitmap可操作的对象

        参数:
        - x (int): 起始点横坐标 (可选)
        - y (int): 起始点纵坐标 (可选)
        - x1 (int): 终止点横坐标 (可选)
        - y1 (int): 终止点纵坐标 (可选)

        返回结果:
        - Bitmap: Java中的Bitmap对象，详细属性请参考：https://developer.android.google.cn/reference/kotlin/android/graphics/Bitmap?hl=en
        """

    @staticmethod
    def file2Bitmap(path: str, sampleSize: int = None) -> Bitmap:
        """
        将图片文件读取为内存图像Bitmap

        参数:
        - path (str): 图片路径地址
        - sampleSize (int): 图像缩放参数 (可选)

        返回结果:
        - Bitmap: Java中的Bitmap对象，详细属性请参考：https://developer.android.google.cn/reference/kotlin/android/graphics/Bitmap?hl=en
        """

    @staticmethod
    def capture(path: str, bitmap: Bitmap = None, quality: int = None) -> Any:
        """
        截图到指定的文件地址

        参数:
        - path (str): 存储的路径
        - bitmap (Bitmap): Android图像 (可选，默认全屏截图)
        - quality (int): 截图的清晰度 (可选，默认为100，原图)

        返回结果:
        - File: Java中的File对象，详细属性请参考：https://tool.oschina.net/uploads/apidocs/jdk-zh/java/io/File.html
        """


class FindColors:
    def __init__(self, colors: str) -> None:
        pass

    def rect(self, x: int, y: int, x1: int, y1: int) -> 'FindColors':
        pass

    def space(self, num: int) -> 'FindColors':
        pass

    def ori(self, num: int) -> 'FindColors':
        pass

    def find(self) -> Optional[Point]:
        pass

    def find_all(self) -> List[Point]:
        pass


class FindImages:
    def __init__(self, part_img: str) -> None:
        pass

    def confidence(self, num: float) -> 'FindImages':
        pass

    def find(self) -> Optional[dict]:
        pass

    def find_all(self) -> List[dict]:
        pass


class Ocr:
    def __init__(self) -> None:
        pass

    def rect(self, x: int, y: int, x1: int, y1: int) -> 'Ocr':
        pass

    def pattern(self, regx: str) -> 'Ocr':
        pass

    def file(self, path: str) -> 'Ocr':
        pass

    def find(self) -> Optional[dict]:
        pass

    def find_all(self) -> List[dict]:
        pass


# Callable[[bool], None]
class CompareColors:
    def __init__(self, colors: str) -> None:
        pass

    def diff(self, color: str) -> 'CompareColors':
        pass

    def until(self) -> 'CompareColors':
        pass

    def asy(self, method) -> 'CompareColors':
        pass

    def compare(self) -> bool:
        pass


class QRcode:
    def __init__(self) -> None:
        pass

    def file(self, path: R) -> 'QRcode':
        pass

    def bitmap(self, bitmap: Bitmap) -> 'QRcode':
        pass

    def find(self) -> Any:
        pass

    def rect(self, x: int, y: int, x1: int, y1: int) -> 'QRcode':
        pass


class yolo_v5_res:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.w = 0.0
        self.h = 0.0
        self.label = ""
        self.prob = 0.0


class yolo_v5:
    def __init__(self, model: str) -> None:
        """
        初始化yolov5 模型

        :param model:可传入模型名称(模型市场中的),也可以传入本地模型路径.
        """
        pass

    def find_all(self) -> 'List[yolo_v5_res]':
        pass
