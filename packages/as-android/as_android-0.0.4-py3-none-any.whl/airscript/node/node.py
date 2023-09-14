from typing import List

from airscript import Selector


class Rect:
    def __init__(self):
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
        pass

    def width(self):
        return 0;

    def height(self):
        return 0;

    def centerX(self):
        return 0;

    def centerY(self):
        return 0;


class Node:
    def __int__(self):
        self.id = ""
        self.text = ""
        self.type = ""
        self.desc = ""
        self.hintText = ""
        self.packageName = ""
        self.rect = Rect()
        self.childCount = 0
        self.inputType = 0
        self.maxTextLength = 0
        self.clickable = True
        self.checkable = True
        self.checked = True
        self.editable = True
        self.enabled = True
        self.visible = True
        self.dismissable = True
        self.focusable = True
        self.focused = True
        self.longClickable = True

        pass

    def find(self, sel: Selector) -> 'Node':
        return self

    def find_all(self, sel: Selector) -> 'List[Node]':
        return [self]

    def click(self):
        return True

    def long_click(self):
        return True

    def slide(self, ori: int):
        """
        滑动

        :param ori: 滑动的方向;
                    -1:向前滑动;
                    1:向后滑动
        """
        return True

    def input(self, msg: str):
        """
        输入信息

        :param msg: 输入的信息
        """
        return True


