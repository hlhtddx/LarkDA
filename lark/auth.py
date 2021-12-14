import webbrowser
from functools import wraps
from urllib.parse import urlencode

from larksuiteoapi.api import APIError
from larksuiteoapi.service.authen.v1 import Service as AuthService, AuthenAccessTokenReqBody, \
    AuthenRefreshAccessTokenReqBody, UserAccessTokenInfo
from requests import ReadTimeout
from requests.exceptions import ProxyError

from utils import logger
from webserver import run_server

ERR_CODE_TOKEN_EXPIRED = 99991677
RETRY_TIMES = 3


class Authentication:
    def __init__(self, login):
        self.tenant = login.tenant
        self.store = login.store
        self.config = login.config
        self.code_returned = ''
        self.is_login = False

    def _store_user_access_token(self, user_token_info: UserAccessTokenInfo) -> None:
        """Store access token to config store"""
        self.store.set('user_access_token', user_token_info.access_token, user_token_info.expires_in)
        self.store.set('refresh_token', user_token_info.refresh_token, user_token_info.refresh_expires_in)
        self.is_login = True

    def _retrieve_token(self, code) -> bool:
        """Retrieve access token from challenge code"""
        body = AuthenAccessTokenReqBody("authorization_code", code)
        auth_service = AuthService(self.config)
        resp = auth_service.authens.access_token(body).do()
        if resp.code == 0:
            self._store_user_access_token(resp.data)
            return True
        logger.error('error error:%s, msg:%s', resp.error, resp.msg)
        return False

    def on_login_success(self, code) -> bool:
        """Retrieve access token from challenge code"""
        self.code_returned = code
        return True

    def _launch_login_url(self) -> None:
        redirect_uri = 'http://127.0.0.1:5555/login_success'
        param = urlencode({'redirect_uri': redirect_uri, 'app_id': self.tenant.app_id, 'state': self.tenant.name})
        login_uri = '''https://open.feishu.cn/open-apis/authen/v1/index?''' + param
        webbrowser.open_new_tab(login_uri)

    @property
    def user_access_token(self) -> str:
        result, user_access_token = self.store.get('user_access_token')
        if result and user_access_token:
            return user_access_token

        user_access_token = self.refresh_token()
        if user_access_token:
            return user_access_token

        self.is_login = False
        return ''

    def login(self) -> bool:
        self.is_login = False
        self.code_returned = ''
        self._launch_login_url()
        run_server(self)
        if self.code_returned:
            self._retrieve_token(self.code_returned)
        return self.is_login

    def logout(self) -> None:
        self.is_login = False
        self.store.set('user_access_token', '', -1)
        self.store.set('refresh_token', '', -1)

    def check_login(self) -> bool:
        return self.refresh_token() != ''

    def refresh_token(self) -> str:
        """Refresh access token"""
        result, refresh_token = self.store.get('refresh_token')
        if not refresh_token:
            return ''

        body = AuthenRefreshAccessTokenReqBody("refresh_token", refresh_token)
        auth_service = AuthService(self.config)
        resp = auth_service.authens.refresh_access_token(body).do()
        if resp.code == 0:
            self._store_user_access_token(resp.data)
            return resp.data.access_token
        else:
            logger.error('error error:%s, msg:%s', resp.error, resp.msg)
            return ''


class LarkCallArguments:
    auth: Authentication or None

    def __init__(self, auth):
        self.auth = auth
        self.config = None
        self.user_access_token = None
        self.service = None


def lark_call(service_factory, uses_user_token=True):
    def outer(func):
        @wraps(func)
        def inner(auth, *args, **kargs):
            largs = LarkCallArguments(auth)
            largs.config = auth.config
            largs.user_access_token = auth.user_access_token if uses_user_token else None
            largs.service = service_factory(largs.config)

            for retry_count in range(RETRY_TIMES):
                if uses_user_token and not largs.user_access_token and not auth.login():
                    auth.is_login = False
                    return None

                resp = None
                try:
                    resp = func(largs, *args, **kargs)
                except APIError as api_error:
                    logger.error('Lark API Error, %s', api_error.message)
                except ReadTimeout as timeout_error:
                    logger.error('Lark API request timeout %s', timeout_error.request)
                except ProxyError as proxy_error:
                    logger.error('Lark API Proxy error %s', proxy_error.strerror)
                except ConnectionError as conn_error:
                    logger.error('Lark API ConnectionError %s', conn_error.strerror)

                if resp is None:
                    logger.error('Unknown error without response')
                    return None

                if uses_user_token and resp.code == ERR_CODE_TOKEN_EXPIRED:
                    logger.warn('Token expired code=%d, msg=%s', resp.code, resp.msg)
                    largs.user_access_token = auth.refresh_token()
                    continue
                elif resp.code != 0:
                    logger.error('Failed to execute func, code=%d, msg=%s', resp.code, resp.msg)
                    return None

                auth.is_login = True
                return resp.data
            return None

        return inner

    return outer
