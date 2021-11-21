import argparse
import sys

from control import Workspace
from control.common import InvalidWorkspaceException
from sub_cmds import all_commands


class Main:
    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(description='DevOps Assistant for Feishu.')

    def prepare_arg_parser(self):
        # global_parser.add_argument('-h', dest='help', action='store_true',
        #                            help='Print help usage message.')
        self.arg_parser.add_argument('--help-all', dest='help_all', action='store_true',
                                     help='Show this help message with all subcommands and exit.')
        self.arg_parser.add_argument('-v', '--version', dest='help', action='store_true',
                                     help='Print help usage message.')
        sub_command_parser = self.arg_parser.add_subparsers(title='Sub command', dest='command',
                                                            description='Sub command')
        for command_cls in all_commands.values():
            command_cls.prepare_arg_parser(sub_command_parser)

    def parse_args(self, argv):
        args = self.arg_parser.parse_args(argv)
        return args

    def main(self, argv):
        self.prepare_arg_parser()
        args = self.parse_args(argv)

        if not args.__contains__('command'):
            print('No command specified')
            return

        command_name = args.command
        try:
            if command_name not in all_commands:
                print('No command ', command_name)
                exit(-1)
            command_cls = all_commands[command_name]

            if command_cls.requires_workspace:
                workspace = Workspace('.', command_name == 'init')
            else:
                workspace = None

            command = command_cls(workspace)
            command.execute(args)
        except InvalidWorkspaceException:
            print('Not in a valid workspace.')
            exit(-1)


if __name__ == '__main__':
    Main().main(sys.argv[1:])
