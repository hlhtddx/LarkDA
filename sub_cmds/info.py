from argparse import ArgumentParser

from control import global_config
from .command import Command


class Info(Command):
    @classmethod
    def prepare_arg_parser(cls, sub_command_parser):
        parser: ArgumentParser = sub_command_parser.add_parser('info')
        parser.add_argument('--all', action='store_true', default=True)
        parser.add_argument('--tenant', action='store_true', default=True)
        parser.add_argument('--login', action='store_true', default=True)
        parser.add_argument('--drive', action='store_true', default=False)

    def execute(self, args):
        if args.all or args.tenant:
            print('List all tenants...')
            for tenant in global_config.tenants.values():
                print(tenant)

        if args.all or args.login:
            print(self.workspace.login)

        if args.all or args.drive:
            print(self.workspace.drive)

        print('Done.')
