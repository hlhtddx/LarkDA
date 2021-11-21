from argparse import ArgumentParser

from control import global_config
from sub_cmds.command import Command
from utils import logger


class Login(Command):
    @classmethod
    def prepare_arg_parser(cls, sub_command_parser):
        parser:ArgumentParser = sub_command_parser.add_parser('login')
        parser.add_argument('-n', '--name', type=str, default='', help='Tenant name to login')
        parser.add_argument('-o', '--out', action='store_true', default=False, help='Logout from current login')
        parser.add_argument('-f', '--force', action='store_true', default=False, help='Force to launch URL to login')

    def validate_args(self, args) -> bool:
        if args.name and args.out:
            logger.error('Cannot specify login name and logout together')
            return False
        return True

    def execute(self, args):
        if args.name:
            return self.login(args.name, args.force)
        elif args.out:
            return self.logout()
        else:
            return False

    def login(self, name, force):
        tenant = global_config.get_tenant(name)
        if not tenant:
            logger.error('Failed to get tenant(%s)', name)
            return False
        self.workspace.login(tenant, force=force)

    def logout(self):
        self.workspace.logout()
