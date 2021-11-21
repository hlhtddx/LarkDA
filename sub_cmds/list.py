from argparse import ArgumentParser
from pathlib import Path

from .command import Command


class List(Command):
    @classmethod
    def prepare_arg_parser(cls, sub_command_parser):
        parser: ArgumentParser = sub_command_parser.add_parser('list')
        parser.add_argument('-r', '--recursive', action='store_true', default=False)
        parser.add_argument('-f', '--no-file', action='store_true', default=False)
        parser.add_argument('-s', '--sync', action='store_true', default=False)
        parser.add_argument('targets', nargs='*', default=None)

    def execute(self, args):
        if not self.workspace.is_login:
            print('MUST login at first')
            return
        if not args.targets:
            args.targets = ['.']
        for target in args.targets:
            self.list(target=target, args=args)

    def list(self, target, args):
        target_path = Path(target).absolute()
        try:
            target_rel_path = target_path.relative_to(self.workspace.path)
        except ValueError as e:
            print('target folder/file is not under workspace. ', target)
            return

        print('List files for folder:', target_rel_path)
        args.indent_level = 0
        self._list_folder(target_rel_path, args)

    def _list_folder(self, rel_path, args):
        args.indent_level += 1

        file = self.drive.find_file_by_path(rel_path)

        if not file or file.doc_type != 'folder':
            print(f'The folder {rel_path} does not exist.')
            return
        if args.sync:
            result, folders, docs = file.refresh_children()
        else:
            result, folders, docs = file.get_children()

        if not result:
            print(f'Failed to retrieve folder({rel_path}) data')
            return

        for folder in folders:
            print(' ' * args.indent_level, folder)
            if args.recursive:
                self._list_folder(rel_path / folder.name, args)
        if not args.no_file:
            for doc in docs:
                if args.sync:
                    doc.refresh()
                print(' ' * args.indent_level, doc)

        args.indent_level -= 1
