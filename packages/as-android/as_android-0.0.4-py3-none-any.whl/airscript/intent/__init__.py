from typing import Any


class Intent:
    def __init__(self, action: str, uri: Any = None, context: Any = None,cls: Any = None):
        pass

    def __init__(self, packageContext: Any, cls: Any):
        pass

    @staticmethod
    def run(tag: str):
        """
        启动APP

        :param tag: 可以是包名,也可以是应用名称
        """
        pass

    @staticmethod
    def browser(tag: str):
        """

        """
        pass
