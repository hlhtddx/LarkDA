from logging import Logger, DEBUG, WARN
import os

debug = os.environ.get('DEBUG', default=False)
debug_level = DEBUG if debug else WARN

logger = Logger('FeishuDA', level=debug_level)