from argparse import ArgumentParser

from .command import Command


class Gui(Command):
    @classmethod
    def prepare_arg_parser(cls, sub_command_parser):
        parser: ArgumentParser = sub_command_parser.add_parser('init')
        parser.add_argument('--clean', action='store_true', default=False)

    def execute(self, args):
        pass
