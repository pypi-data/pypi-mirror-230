from ebooklib import epub


def add_nav_for_epub(book, output='output.epub', position=1, title='目录', file_name='nav.xhtml', uid='nav'):
    """为 EPUB 添加目录页面，方便解包后在浏览器中 查看、操作

    :param book: epub 电子书文件（路径）
    :param output: 输出的 epub 电子书文件（路径）
    :param position:
        插入目录的位置默认为 1，即第一页（封面）之后

        要插入到最后，请给一个很大的数字

        支持负数操作，例如给 -1 为倒数第一页之后。
    :param title: 目录标题，不知道就不用管
    :param file_name: 添加目录页面的文件名，不知道就不用管
    :param uid: 添加目录页面的唯一标识，不知道就不用管
    :return:
    """
    book = epub.read_epub(book, options={
        'ignore_ncx': True,
    })
    book.add_item(epub.EpubNav(file_name=file_name))

    if len(book.spine) <= position:
        book.spine.append('nav')  # 固定 "nav"
    else:
        book.spine.insert(position, 'nav')

    if len(book.toc) <= position:
        book.toc.append(epub.Link(file_name, title, uid))
    else:
        book.toc.insert(position, epub.Link(file_name, title, uid))

    epub.write_epub(output, book)

    return 'Done!'
