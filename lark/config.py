from typing import Tuple
from larksuiteoapi import Store
from utils.config import SqliteConfig


class DaStore(Store):
    def __init__(self, prefix, config):  # type: (str, SqliteConfig) -> None
        self.prefix = prefix
        self.config = config

    def get(self, key):  # type: (str) -> Tuple[bool, str]
        value = self.config.get(f'{self.prefix}.{key}')
        if value:
            return True, value
        return False, ''

    def set(self, key, value, expire):  # type: (str, str, int) -> None
        """
        storage key, value into the store, value has an expire time.(unit: second)
        """
        self.config.set(f'{self.prefix}.{key}', value, expire)
