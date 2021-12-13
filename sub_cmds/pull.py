from argparse import ArgumentParser
from pathlib import Path

from .command import Command


class Pull(Command):
    INDENT_SPACE = '  '

    @classmethod
    def prepare_arg_parser(cls, sub_command_parser):
        parser: ArgumentParser = sub_command_parser.add_parser('pull')
        parser.add_argument('-r', '--recursive', action='store_true', default=False)
        parser.add_argument('-s', '--sync', action='store_true', default=False)
        parser.add_argument('-m', '--media', action='store_true', default=False)
        parser.add_argument('targets', nargs='*', default=None)

    def execute(self, args):
        if not self.workspace.is_login:
            print('MUST login at first')
            return
        if not args.targets:
            args.targets = ['.']
        for target in args.targets:
            self.pull(target=target, args=args)

    def pull(self, target, args):
        target_path = Path(target).absolute()
        try:
            target_rel_path = target_path.relative_to(self.workspace.path)
        except ValueError as e:
            print('target folder/file is not under workspace. ', target)
            return

        print('Pulling folder:', target_rel_path)
        args.indent_level = 0
        self._pull_folder(target_rel_path, args)

    def _pull_folder(self, rel_path, args):

        file = self.drive.find_file_by_path(rel_path)

        if not file or file.doc_type != 'folder':
            print(f'The folder {rel_path} does not exist.')
            return

        # Begin to pull a folder
        print(self.INDENT_SPACE * args.indent_level, file)
        args.indent_level += 1

        if args.sync:
            result, folders, docs = file.refresh_children()
        else:
            result, folders, docs = file.get_children()

        if not result:
            print(f'Failed to pull folder({rel_path})')
            return

        abs_path = (self.workspace.path / rel_path).absolute()
        try:
            abs_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print('Failed to mkdir ', abs_path, 'Err=', e.strerror)
            return

        if args.recursive:
            for folder in folders:
                self._pull_folder(rel_path / folder.name, args)

        for doc in docs:
            if args.sync:
                doc.refresh()
            print(self.INDENT_SPACE * args.indent_level, doc)
            doc.pull(args.media)
            doc.link_to(abs_path)
            print(self.INDENT_SPACE * args.indent_level, ' done')

        args.indent_level -= 1
        print(self.INDENT_SPACE * args.indent_level, ' done')

