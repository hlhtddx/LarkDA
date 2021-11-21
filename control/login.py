from larksuiteoapi import DOMAIN_FEISHU, Config as LarkConfig

from control.common import Tenant
from lark.auth import Authentication
from lark.config import DaStore as Store
from utils import logger, debug_level
from utils.config import SqliteConfig


class Login:
    def __init__(self, config: SqliteConfig, tenant: Tenant):
        assert tenant
        self.tenant = tenant
        self.config = config
        self.store = Store(prefix=tenant.name, config=config)
        app_settings = LarkConfig.new_internal_app_settings(app_id=tenant.app_id, app_secret=tenant.app_secret)
        self.config = LarkConfig.new_config(DOMAIN_FEISHU, app_settings, logger, debug_level, self.store)
        self.auth = Authentication(login=self)

    def __str__(self):
        return f'Login: tenant={self.tenant.name}, is_login={self.is_login}'

    @property
    def name(self):
        if self.tenant:
            return self.tenant.name
        else:
            return None

    def login(self, force):
        """Check if login. if not, launch login page towards"""
        if not force and self.auth.check_login():
            return True
        return self.auth.login()

    def logout(self):
        """Clear access tokens"""
        self.auth.logout()

    def refresh(self) -> str:
        """Refresh user access token using refresh token"""
        return self.auth.refresh_token()

    @property
    def user_access_token(self) -> str:
        return self.auth.user_access_token

    @property
    def is_login(self) -> bool:
        return bool(self.user_access_token)
