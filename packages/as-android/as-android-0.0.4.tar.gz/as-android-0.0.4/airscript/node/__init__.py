from typing import Union, List

from airscript.node.node import Node


class Selector:
    def __init__(self, mode: int = 0):
        pass

    def find(self) -> Node:
        pass

    def until_find(self) -> Node:
        pass

    def find_all(self) -> List[Node]:
        pass

    def until_find_all(self) -> List[Node]:
        pass

    def id(self, nid: str) -> 'Selector':
        pass

    def text(self, ntext: str) -> 'Selector':
        pass

    def type(self, ntype: str) -> 'Selector':
        pass

    def desc(self, ndesc: str) -> 'Selector':
        pass

    def hintText(self, nhintText: str) -> 'Selector':
        pass

    def packageName(self, npackageName: str) -> 'Selector':
        pass

    def path(self, pathstr: str) -> 'Selector':
        pass

    def inputType(self, ntype: int) -> 'Selector':
        pass

    def depth(self, ntype: int) -> 'Selector':
        pass

    def drawingOrder(self, ntype: int) -> 'Selector':
        pass

    def childCount(self, nccount: int) -> 'Selector':
        pass

    def inputType(self, ninputtype: int) -> 'Selector':
        pass

    def maxTextLength(self, nmax: int) -> 'Selector':
        pass

    def clickable(self, nclickable: bool) -> 'Selector':
        pass

    def checkable(self, ncheckable: bool) -> 'Selector':
        pass

    def checked(self, nchecked: bool) -> 'Selector':
        pass

    def editable(self, neditable: bool) -> 'Selector':
        pass

    def enabled(self, nenabled: bool) -> 'Selector':
        pass

    def dismissable(self, ndismissable: bool) -> 'Selector':
        pass

    def focusable(self, nfocusable: bool) -> 'Selector':
        pass

    def focused(self, nfocused: bool) -> 'Selector':
        pass

    def longClickable(self, nlongClickable: bool) -> 'Selector':
        pass

    def visible(self, nvisible: bool) -> 'Selector':
        pass

    def parent(self, *n: Union[float, int]) -> 'Selector':
        """
        获取父控件

        :param n: 获取第n个父元素,默认获取所有父元素
                        (2):获取爷爷元素
                        (3):获取太爷爷元素
                        (1,3):获取第1和第3个父元素
                        (1.3):获取第1-3 之间的所有父元素
        """
        pass

    def child(self, *n: Union[float, int]) -> 'Selector':
        """
        获取孩子控件

        :param n:可以填写多个数字
                不填写任何参数,获取所有孩子控件;
                当数字为正整数(例如1):获取第1个孩子控件;
                当数字为负整数(例如:-1) 获取倒数第1个孩子;
                当数字为正小数(例如:1.3):获取1-3之间的所有孩子;
                当数字为负小数(例如:-1.3):获取倒数 1-3之间的所有孩子;
        """
        pass

    def brother(self, *n: Union[float, int]) -> 'Selector':
        """
        获取兄弟控件

        :param n: 获取第n个兄弟控件|
                () 默认不填:获取所有兄弟控件|
                (1) 获取第一个兄弟控件 |
                (1,2) 获取第1和第2个兄弟控件|
                (1.4) 获取1-4之间的所有兄弟控件|
                (0.1) 获取当前控件的下一个兄弟控件|
                (-0.1) 获取当前空间的上一个兄弟控件|
                (-1) 获取倒数第1个兄弟控件
        """
        pass


