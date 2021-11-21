import json
import os
from pathlib import Path

from utils import logger


class PullDataParser:
    def __init__(self, callback, param):
        self.callback = callback
        self.param = param

    def __parse_dict(self, source_node: dict, target_node: dict):
        type = source_node.get('type', '')
        if type == 'diagram':
            return None
        elif type == 'gallery':
            pass

        for key, value in source_node.items():
            if key == 'imageList':
                self.callback.pull_image_list(self.param, value)
            elif key == 'file':
                self.callback.pull_attached_file(self.param, value)
            elif key == 'location':
                continue
            new_item = self.__parse_item(value)
            if new_item is not None:
                target_node[key] = new_item

    def __parse_list(self, source_node: list, target_node: list):
        for item in source_node:
            new_item = self.__parse_item(item)
            if new_item is not None:
                target_node.append(new_item)

    def __parse_item(self, source_item):
        target_item = source_item
        if isinstance(source_item, dict):
            target_item = {}
            self.__parse_dict(source_item, target_item)
        elif isinstance(source_item, list):
            target_item = []
            self.__parse_list(source_item, target_item)
        return target_item

    def parse(self, source: dict):
        return self.__parse_item(source)


class Pull:
    def __init__(self, file_manager):
        self.all_paths = set()
        self.all_file = {}
        self.all_paths.add('.')
        self.media_list = {}
        self.file_manager = file_manager

    def pull(self, target_dir):
        """Walk through My space and folder list, and download all found doc"""

        def pull_doc_internal(folder, files, __unused__):
            for file in files:
                self.pull_doc(file.token, target_dir, folder.path, file.name)

        self.file_manager.virtual_root.walk(pull_doc_internal, None)
        self.store_file_info(target_dir)

    def store_file_info(self, target_dir):
        old_file_info_path = os.path.join(target_dir, 'source_info.json')
        new_file_info_path = os.path.join(target_dir, 'files.json')
        if os.path.isfile(old_file_info_path) and not os.path.exists(new_file_info_path):
            os.rename(src=old_file_info_path, dst=new_file_info_path)
        else:
            with open(new_file_info_path, 'w') as fp:
                info = {'folders': list(self.all_paths), 'files': self.all_file}
                fp.write(json.dumps(info, ensure_ascii=False))

    @staticmethod
    def __make_dir(path):
        Path(path).mkdir(parents=True, exist_ok=True)

    def post_pull_doc(self, target_path, content) -> None:
        source_root = json.loads(content)
        self.media_list.clear()
        PullDataParser(self, target_path).parse(source_root)

    @staticmethod
    def is_file_valid(file_path, min_size=0):
        return os.path.isfile(file_path) and os.path.getsize(file_path) > min_size

    def pull_doc(self, token, target_dir, rel_path, base_name):
        """Download doc and all attachment into a local folder"""
        if not base_name:
            base_name = token
        doc = self.file_manager.get_item(token)
        if doc is None or doc.doc_type != 'doc':
            logger.warn('Incorrect file type')
            return False

        doc_path_current = os.path.join(target_dir, rel_path, base_name + '.fdoc_v2')

        print(f'Pull doc {rel_path}/{base_name}')

        self.all_file[token] = {'path': doc_path_current, 'token': token, 'name': base_name, 'type': 'doc'}
        self.__make_dir(doc_path_current)

        content_path = os.path.join(doc_path_current, 'content.json')
        if self.is_file_valid(content_path, 20):
            with open(content_path, 'r') as fp:
                content = fp.read()
        else:
            content = doc.get_content()
            if content is None:
                logger.error('failed to pull doc %s', doc_path_current)
                print('Failed')
                return False
            with open(content_path, 'w') as fp:
                print('Done')
                fp.write(content)

        self.post_pull_doc(doc_path_current, content)
        with open(os.path.join(doc_path_current, 'media_list.json'), 'w+') as fp:
            json.dump(self.media_list, fp, ensure_ascii=False)
        return True

    def pull_image_list(self, target_path, image_list):
        """Download imageList inside doc"""
        for image in image_list:
            token = image['fileToken']
            file_name = f'{token}.png'
            content_path = os.path.join(target_path, file_name)

            media_info = {'path': target_path, 'token': token, 'name': file_name, 'type': 'png'}
            self.all_file[token] = media_info
            self.media_list[token] = media_info

            if self.is_file_valid(content_path, 20):
                logger.info('Media %s is downloaded. skip it', token)
                continue

            file = self.file_manager.get_item(token)
            if file is None or file.doc_type != 'media':
                return

            content = file.get_content()
            if content is None:
                return False
            with open(content_path, 'wb') as fp:
                fp.write(content)

    def pull_attached_file(self, target_path, item):
        """Download attachment inside doc"""
        token = item['fileToken']
        file_name = item['fileName']

        content_path_v1 = os.path.join(target_path, f'{token}.bin')
        content_path_current = os.path.join(target_path, token, file_name)

        self.__make_dir(os.path.dirname(content_path_current))

        media_info = {'path': os.path.join(target_path, token), 'token': token, 'name': file_name, 'type': 'file'}
        self.all_file[token] = media_info
        self.media_list[token] = media_info

        if self.is_file_valid(content_path_v1, 20):
            logger.info('Media %s is downloaded for v1. Reuses it', token)
            os.rename(content_path_v1, content_path_current)
            return True
        elif self.is_file_valid(content_path_current, 20):
            logger.info('Media %s is downloaded. Skip it', token)
            return True

        try:
            file = self.file_manager.get_item(token)
            if file is None or file.doc_type != 'media':
                return

            content = file.get_content()
            if content is None:
                return False
        except Exception as err:
            logger.error(err)
            return False

        with open(content_path_current, 'wb') as fp:
            fp.write(content)
        return True


def pull(tenant):
    Pull(tenant.drive).pull(tenant.local_path)
