import json
import time
from utils import logger

from pathlib import Path
from threading import Lock
from typing import Dict, Tuple
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError


class JsonConfig:
    def __init__(self, config_file):  # type: (Path) -> None
        logger.debug('Init a json config file', config_file)
        self.data = {}  # type: Dict[str, Tuple[object, int]]
        self.mutex = Lock()  # type: Lock
        self.config_file = config_file

        try:
            with self.config_file.open(mode='r') as fp:
                self.data = json.load(fp)
        except OSError:
            self.data = {}

    def get(self, key):  # type: (str) -> object
        """
        retrieve storage key, value from the store, value has an expire time.(unit: second)
        """
        self.mutex.acquire()
        logger.debug('Get config from json(key=%s)', key)
        try:
            val = self.data.get(key)
            if val is None:
                return False, ""
            else:
                if 0 < val[1] < int(time.time()):
                    self.data.pop(key)
                    return None
                else:
                    return val[0]
        finally:
            self.mutex.release()

    def set(self, key, value, expire=-1):  # type: (str, object, int) -> None
        """
        storage key, value into the store, value has an expire time.(unit: second)
        """
        self.mutex.acquire()
        logger.debug('Set config to json(key=%s, value=%s, expire=%d)', key, value, expire)
        try:
            if expire > 0:
                expire += time.time()
            self.data[key] = (value, expire)
        finally:
            self.mutex.release()
        with self.config_file.open(mode='w+') as fp:
            json.dump(self.data, fp, ensure_ascii=False, indent=True)


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
        retrieve storage key, value from the store, value has an expire time.(unit: second)
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
        storage key, value into the store, value has an expire time.(unit: second)
        """
        logger.debug('Set config to sqlite(key=%s, value=%s, expire=%d)', key, value, expire)
        if expire > 0:
            expire += time.time()
        self.config.insert_all([{'key': key, 'value': value, 'expires': expire}], replace=True)
