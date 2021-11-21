import cmd
from functools import wraps

from control import Workspace, pull, push


def parse_args(arg: str, min_args, max_args=-1):
    if min_args == 0 and arg == '':
        return True, []

    args = arg.split(' ')

    if max_args < 0:
        max_args = min_args

    if min_args <= len(args) <= max_args:
        return True, args

    if max_args == min_args:
        print(f'Arguments count MUST be {min_args}')
    else:
        print(f'Arguments count MUST be between {min_args} and {max_args}')
    return False, None


def check_login(min_args, max_args=-1):
    def outer(func):
        @wraps(func)
        def wrapper(instance, arg):
            result, args = parse_args(arg, min_args, max_args)
            if not result:
                return

            if instance.tenant is None or not instance.tenant.is_login:
                print('MUST login at first')
                return

            func(instance, args)

        return wrapper

    return outer


def check_workspace(min_args, max_args=-1):
    def outer(func):
        @wraps(func)
        def wrapper(instance, arg):
            result, args = parse_args(arg, min_args, max_args)
            if not result:
                return

            if instance.workspace is None:
                print('MUST set workspace at first')
                return

            if args is None:
                func(instance, args)
            else:
                func(instance, *args)

        return wrapper

    return outer


class DevopsAssistShell(cmd.Cmd):
    intro = 'Welcome to the Devops Assistant shell.   Type help or ? to list commands.\n'
    prompt = '(devops)/~ '

    def __init__(self):
        super().__init__()
        self.workspace = None
        self.tenant = None
        self.update_prompt()

    def update_prompt(self):
        workspace = '-' if not self.workspace else str(self.workspace.path)
        if self.tenant:
            tenant = self.tenant.name
            login = 'On' if self.tenant.is_login else 'Off'
            remote_path = 'PATH'
        else:
            tenant = '-'
            login = 'Off'
            remote_path = '?'
        self.prompt = ':'.join((workspace, tenant, login, remote_path, '~ '))

    def init_workspace(self):
        self.init_tenant()

    def init_tenant(self):
        tenant_name = self.workspace.get_config('tenant')
        self.tenant = self.workspace.get_tenant(tenant_name=tenant_name)
        return self.tenant

    # ----- authentication commands -----
    def do_ws(self, arg):
        """Set workspace path"""
        result, args = parse_args(arg, 0, 1)
        if not result:
            return
        #
        # if len(args) > 0 and self.workspace:
        #     if self.workspace.local_path.samefile(args[0]):
        #         print('Already in workspace ', arg)
        #         return

        try:
            self.workspace = Workspace(*args)
            self.init_workspace()
            if self.tenant:
                self.tenant._login()
            self.update_prompt()
            print('Succeeded to set workspace')
        except OSError as err:
            self.workspace = None
            print('Failed to set workspace', err)

    @check_workspace(0)
    def do_lt(self, arg):
        """List all available tenants for DA"""
        tenants = self.workspace.get_all_tenants()
        for tenant in tenants.values():
            print(tenant.name, ': APP_ID=', tenant.app_id, ' Login:', tenant.is_login)
        print('Done')

    @check_workspace(1)
    def do_login(self, arg):
        """Launch a browser to login to Feishu account. Tenant MUST be specified."""
        tenant = self.workspace.get_tenant(arg)
        if not tenant:
            print('No such tenant')
            self.update_prompt()
            return

        self.tenant = tenant
        self.workspace.set_config('tenant', tenant.name)
        if self.tenant._login():
            print('Login successfully')
        else:
            print('Login failed')
        self.update_prompt()

    @check_login(0)
    def do_logout(self, arg):
        """Launch a browser to login to Feishu account. Tenant MUST be specified."""
        self.tenant.logout()
        self.update_prompt()

    @check_workspace(0)
    def do_whoami(self, arg):
        """Check current tenant that is logged in."""
        if self.tenant is None:
            print('It is not logged in yet.')
        else:
            print(f'{self.tenant.name} is logged in.')

    @check_login(0)
    def do_refresh(self, arg):
        """Refresh access token."""
        if self.tenant.refresh():
            print('Refresh done')
        else:
            print('Refresh failed')
        self.update_prompt()
    #
    # @check_workspace(1)
    # def do_chl(self, arg):
    #     """Change current tenant to new one. Tenant MUST be specified."""
    #     tenant = self.workspace.get_tenant(*arg)
    #     if not tenant:
    #         print('No such tenant')
    #         return
    #
    #     self.tenant = tenant
    #     self.update_prompt()

    # ----- Drive sync commands -----
    @check_login(0)
    def do_pull(self, arg):
        """Re-download all feishu documents to new workspace"""
        pull(self.tenant)

    @check_login(2)
    def do_push(self, arg):
        """Download all feishu documents to new workspace"""
        push(*arg)

    # ----- Drive test commands -----
    @check_login(2, 2)
    def do_fetch(self, arg):
        """Try to fetch a doc, image or attachment"""
        file_manager = self.tenant.drive
        if file_manager.download(*arg) is not None:
            print('succeeded to get content')
        else:
            print('failed to download ')

    @check_login(2)
    def do_mkdir(self, arg):
        """Try to create a new dir in test folder"""
        file_manager = self.tenant.drive
        token = file_manager.create_folder(*arg)
        if not token:
            print('failed to get content')
        else:
            print('succeeded to upload doc, token = ', token)

    @check_login(1)
    def do_doc(self, arg):
        """Try to create a new doc in test folder"""
        file_manager = self.tenant.drive
        token = file_manager.upload_doc(*arg)
        if not token:
            print('failed to get content')
        else:
            print('succeeded to upload doc, token = ', token)

    @check_login(2)
    def do_image(self, arg):
        """Try to upload a image to doc"""
        file_manager = self.tenant.drive
        file = file_manager.upload_media(*arg)
        if not file:
            print('failed to upload image')
        else:
            print('succeeded to upload image:', file.token)

    @check_login(2)
    def do_att(self, arg):
        """Try to upload a attachment to doc"""
        file_manager = self.tenant.drive
        file = file_manager.upload_media(*arg)
        if not file:
            print('failed to upload file')
        else:
            print('succeeded to upload file:', file.token)

    @check_login(0)
    def do_ls(self, arg):
        """List all files and folder under in current path"""
        file_manager = self.tenant.drive
        res, folders, files = file_manager.list()
        if not res:
            print('Failed to list child files')
        else:
            for file in folders + files:
                print(file)

    @check_login(1)
    def do_cd(self, arg):
        """Change to specified folder."""
        file_manager = self.tenant.drive
        res, new_folder = file_manager.change_current_folder(*arg)
        if not res:
            print('failed to change folder to ', *arg)
        self.update_prompt()

    @check_login(0)
    def do_tree(self, arg):
        """Change to sub folder."""
        file_manager = self.tenant.drive
        file_manager.list_all_folders()

    @check_login(0)
    def do_pwd(self, arg):
        """Log out from current Feishu account"""
        file_manager = self.tenant.drive
        print(file_manager.current_path)

    def do_exit(self, arg):
        """Quit and stop the program."""
        print('Thank you for using Devops Assistant shell')
        if self.workspace:
            self.workspace.close()
        return True

    def precmd(self, line):
        return line


def main():
    DevopsAssistShell().cmdloop()


if __name__ == '__main__':
    main()
