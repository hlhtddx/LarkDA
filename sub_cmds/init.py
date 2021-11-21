import shutil
from pathlib import Path

from control import Workspace
from sub_cmds.command import Command


class Init(Command):
    requires_workspace = False

    @classmethod
    def prepare_arg_parser(cls, sub_command_parser):
        parser = sub_command_parser.add_parser('init')
        parser.add_argument('--clean', action='store_true', default=False)

    def execute(self, args):
        print('Initialize workspace.')
        try:
            fda_path = Path('.fda')
            if args.clean:
                shutil.rmtree(fda_path)
            workspace = Workspace(create=True)
        except AttributeError as e:
            print('Failed to create workspace.', e.args)
            return
        print('Done')
