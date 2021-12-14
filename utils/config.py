import json
import time
from utils import logger

from pathlib import Path
from threading import Lock
from typing import Dict, Tuple
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError


class SqliteConfig:
    def __init__(self, database):  # type: (Database) -> None
        """Init workspace using opened database"""
        logger.debug('Init a sqlite config file', database)
        self.database = database
        self.config = self.database['config']
        if 'config' not in self.database.table_names():
            self.config.create({
                'key': str,
                'value': str,
                'expires': int
            }, pk='key')

    def get(self, key):  # type: (str) -> str
        """
        retrieve storage key, value from the store, value has an expired time.(unit: second)
        """
        try:
            logger.debug('Get config from sqlite(key=%s)', key)
            values = self.config.get(pk_values=key)
            if 0 < values['expires'] < int(time.time()):
                self.config.delete(pk_values=key)
                return ''
            else:
                return values['value']
        except NotFoundError:
            return ''

    def set(self, key, value, expire=-1):  # type: (str, str, int) -> None
        """
        storage key, value into the store, value has an expired time.(unit: second)
        """
        logger.debug('Set config to sqlite(key=%s, value=%s, expire=%d)', key, value, expire)
        if expire > 0:
            expire += time.time()
        self.config.insert_all([{'key': key, 'value': value, 'expires': expire}], replace=True)
