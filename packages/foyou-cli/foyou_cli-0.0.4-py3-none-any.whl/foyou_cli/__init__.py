__title__ = 'foyou-cli'
__author__ = 'foyoux'
__version__ = '0.0.4'
__url__ = 'https://github.com/foyoux/foyou-cli'
__ide__ = 'PyCharm - https://www.jetbrains.com/pycharm/'

import fire

from .ebook import add_nav_for_epub
from .aliyundrive import download_by_idm


def version():
    """显示版本信息"""
    return f'{__title__}({__version__}) by {__author__}({__url__})'


def main():
    fire.Fire({
        'epub': add_nav_for_epub,
        'alidown': download_by_idm,
        'version': version,
    })
