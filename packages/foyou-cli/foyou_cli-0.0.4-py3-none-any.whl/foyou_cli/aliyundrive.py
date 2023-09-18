import logging
import os
import re
from pathlib import Path

import psutil
from aligo import Aligo, BaseFile


def del_special_symbol(s: str) -> str:
    """删除Windows文件名中不允许的字符"""
    return re.sub(r'[:*?"<>|]', '_', s)


def download_by_idm(parent_file_id: str, drive_id: str = None, download_path: str = None):
    """使用 IDM 下载文件

    :param parent_file_id: 阿里云盘文件夹文件ID
    :param drive_id: drive_id, 默认 备份盘，res 为资源盘
    :param download_path: 下载路径，默认用户下载目录下 AliyunDrive 文件夹
    :return:
    """
    a = [i.exe() for i in psutil.process_iter() if i.name() == 'IDMan.exe']
    if a:
        idm: str = a[0]
    else:
        print('IDM 未运行')
        exit(1)

    if download_path is None:
        download_path = Path.home() / 'Downloads/AliyunDrive/'

    ali = Aligo(level=logging.ERROR)

    # 处理 drive_id
    if drive_id == 'res':
        drive_id = ali.v2_user_get().resource_drive_id

    # 创建 parent_file_id 文件夹
    folder = ali.get_file(file_id=parent_file_id, drive_id=drive_id)
    download_path = download_path / del_special_symbol(folder.name)

    def callback(file_path: str, file: BaseFile):
        file.name = del_special_symbol(file.name)
        file_path = del_special_symbol(file_path)
        (download_path / file_path).mkdir(parents=True, exist_ok=True)
        cmd = f'{idm} /a /n /d "{file.download_url}" /p "{download_path / file_path}" /f "{file.name}"'
        print(cmd)
        if os.path.exists(idm.replace('"', '')):
            os.system(cmd)
            os.system(f'{idm} /s')

    os.system('chcp 65001')
    ali.walk_files(callback, parent_file_id=parent_file_id, drive_id=drive_id)
