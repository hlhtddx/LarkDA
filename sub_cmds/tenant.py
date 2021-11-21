from argparse import ArgumentParser

from control import global_config
from sub_cmds.command import Command
from utils import logger


class Tenant(Command):
    requires_workspace = False

    @classmethod
    def prepare_arg_parser(cls, sub_command_parser):
        parser: ArgumentParser = sub_command_parser.add_parser('tenant')
        parser.add_argument('-a', '--add', type=str, default='')
        parser.add_argument('-d', '--delete', type=str, default='')
        parser.add_argument('-l', '--list_tenants', action='store_true', default=False)
        parser.add_argument('-i', '--app_id', type=str, default='')
        parser.add_argument('-s', '--app_secret', type=str, default='')
        parser.add_argument('-f', '--force', action='store_true', default=False, help='Force to launch URL to login')

    def validate_args(self, args) -> bool:
        if args.add and args.delete:
            logger.error('不能同时添加和删除tenant')
            return False
        if args.add and (not args.app_id or not args.app_secret):
            logger.error('添加tenant时，必须指定app_id和app_secret')
            return False
        return True

    def execute(self, args):
        if args.add:
            return self.add(args.add, args.app_id, args.app_secret, args.force)
        elif args.delete:
            return self.delete(args.delete)
        elif args.list_tenants:
            return self.list_tenants()
        else:
            return False

    def add(self, name, app_id, app_secret, force):
        if global_config.set_tenant(name, app_id, app_secret):
            print("Successfully add tenant:", name)
        else:
            print("Failed add tenant:", name)

    def delete(self, name):
        if global_config.delete_tenant(name):
            print("Successfully delete tenant:", name)
        else:
            print("Failed delete tenant:", name)

    def list_tenants(self):
        print('List all tenants...')
        for tenant in global_config.tenants.values():
            print(tenant)
        print('Done.')
