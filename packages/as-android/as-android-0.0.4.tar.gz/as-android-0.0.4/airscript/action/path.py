# 手势-创建路径
from typing import Self


class path:
    def __init__(self, startTime=0, duration=20, willContinue=False):
        """
        创建一个新的路径对象

        参数:
        - startTime (number): 延迟多久开始绘制路径，单位ms，默认为0
        - duration (number): 路径绘制的时长，单位ms，默认为20
        - willContinue (boolean): 在路径结束后，手指是否抬起，默认为False
        """

    def moveTo(self, x:int, y:int) -> None:
        """
        移动初始点到指定位置

        参数:
        - x (number): X轴坐标
        - y (number): Y轴坐标
        """
        pass

    def lineTo(self, x: int, y: int)-> None:
        """
        画直线到指定位置

        参数:
        - x (number): X轴坐标
        - y (number): Y轴坐标
        """
        pass

    def quadTo(self, x1: int, y1:int, x2:int, y2:int)-> None:
        """
        使用二次贝塞尔曲线绘制路径

        参数:
        - x1 (number): 控制点1的X轴坐标
        - y1 (number): 控制点1的Y轴坐标
        - x2 (number): 控制点2的X轴坐标
        - y2 (number): 控制点2的Y轴坐标
        """
        pass




