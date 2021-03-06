import logging
from pathlib import Path

from sqlite_utils import Database

from lark.drive import DriveManager
from utils import debug_level
from utils.config import SqliteConfig
from .common import FDA_PATH, global_config, InvalidWorkspaceException
from .login import Login


class Workspace:
    def __init__(self, path_name: str = '.', create: bool = False):
        if create:
            self.__local_path = Path(path_name).absolute()
        else:
            self.__local_path = self.init_local_path(path_name)
        if not self.__local_path:
            raise InvalidWorkspaceException()
        self.init_config_path()
        self.logger = self.init_logger(filename=self.log_path, level=debug_level)
        self.database = Database(self.db_path)
        self.config = SqliteConfig(database=self.database)
        self._login = self.init_login()
        if self.is_login:
            self.drive = DriveManager(workspace=self, login=self._login)
            self.drive.on_login_complete()
        else:
            self.drive = None

    @property
    def path(self) -> Path:
        return self.__local_path

    @property
    def config_path(self) -> Path:
        return self.__local_path / FDA_PATH

    @property
    def db_path(self) -> Path:
        return self.config_path / 'db.sqlite'

    @property
    def doc_path(self) -> Path:
        return self.config_path / 'doc'

    @property
    def log_path(self) -> Path:
        return self.config_path / 'local.log'

    # Initializer for config(local path, tenants info, etc.)
    @staticmethod
    def init_logger(filename, level):
        logger = logging.getLogger("FDA")
        logger.setLevel(level=logging.DEBUG)
        handler = logging.FileHandler(filename)
        handler.setLevel(level=logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def init_local_path(path_name: str) -> Path or None:
        assert path_name
        origin_path = Path(path_name).absolute()
        path = origin_path
        while path != path.anchor and path != Path.home():
            config_path = path / FDA_PATH
            if config_path.is_dir():
                return path
            path = path.parent
        return None

    def init_config_path(self) -> None:
        self.config_path.mkdir(exist_ok=True)

    def init_login(self) -> Login or None:
        tenant = global_config.get_tenant(self.config.get('tenant'))
        if tenant:
            return Login(config=self.config, tenant=tenant)
        return None

    def close(self):
        self.config = None
        self.database.conn.close()

    def login(self, tenant, force):
        if not self._login or tenant != self._login.tenant:
            self._login = Login(self.config, tenant)
            self.config.set('tenant', tenant.name)

        if self._login.login(force):
            pass
            # self.drive.on_login_complete()

    def logout(self):
        if self._login.logout():
            self.config.set('tenant', '')

    @property
    def is_login(self):
        if not self._login:
            return False
        return self._login.is_login

    def find_file(self, path: Path) -> object or None:
        parent = self.find_file(path.parent)
        if not parent:
            return None
        file_name = path.name
        if file_name.endswith('fdoc_v2'):
            # file is doc
            pass
        return parent.find_child(file_name)
