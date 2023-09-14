from typing import Union


class Kv:
    def save(self, key: str, value: Union[str, bool, int]) -> None:
        pass

    def get(self, key: str) -> Union[str, bool, int]:
        pass
