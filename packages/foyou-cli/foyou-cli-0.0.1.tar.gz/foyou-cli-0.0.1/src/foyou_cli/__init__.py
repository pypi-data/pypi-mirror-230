__title__ = 'foyou-cli'
__author__ = 'foyoux'
__version__ = '0.0.1'

import fire

from .ebook import add_nav_for_epub


def main():
    fire.Fire({
        'epub': add_nav_for_epub,
    })
