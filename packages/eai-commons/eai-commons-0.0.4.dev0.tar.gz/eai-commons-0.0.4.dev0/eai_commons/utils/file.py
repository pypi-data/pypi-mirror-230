import os
import json
import tempfile
import fcntl
import csv

from typing import Any, Dict, Optional, List

from eai_commons.logging import logger


def file_relative_path(dunderfile: str, relative_path: str) -> str:
    """
    Return the relative path of a file to another file.

    Example:
        ``path_ = file_relative_path(__file__, "../error/errors.py")``

        You can get the absolute path from path.py to errors.py.
    """
    return os.path.join(os.path.dirname(dunderfile), relative_path)


def get_file_extension(file: str) -> str:
    """
    Return the extension of a file.

    Example:
        ``extension = get_file_extension("/opt/code/file.py")``

        The extension is ``.py``
    """
    return os.path.splitext(file)[1].lower()


def load_json_file(path: str) -> list | dict:
    """
    Load a json file.

    Example:
        ``data = load_json_file("/opt/code/file.json")``
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def create_directory(directory_path, lockfile: Optional[str] = None):
    """
    创建目录，通过加锁机制，避免多进程下并发创建失败的问题
    :param directory_path: 目录的绝对地址
    :param lockfile: 锁路径，默认为临时目录下的.eai_commons.lock
    :return:
    """

    if lockfile is None:
        lockfile = f"{tempfile.gettempdir()}/.eai_commons.lock"

    with open(lockfile, "w") as lockfile:
        fcntl.flock(lockfile, fcntl.LOCK_EX)
        try:
            os.makedirs(directory_path, exist_ok=True)
        except FileExistsError:
            pass
        finally:
            fcntl.flock(lockfile, fcntl.LOCK_UN)


def csv_file_to_dicts(dest_file_path: str, encoding="utf-8") -> list[str] | None:
    """
    csv 以字典列表形式返回
    :param dest_file_path: csv文件绝对路径
    :param encoding: 编码，默认以utf-8解析
    :return:
    """
    if (
        not dest_file_path
        or get_file_extension(dest_file_path).lower() != ".csv"
        or not os.path.exists(dest_file_path)
    ):
        logger.warn(
            "dest_file_path is None, or dest_file is not `csv`, or dest_file is not exist!"
        )
        return None

    with open(dest_file_path, "r", encoding=encoding) as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def dicts_to_csv_file(dest_file_path: str, dicts: list[dict]) -> bool:
    """
    字典列表写入csv文件
    :param dest_file_path: csv文件绝对路径
    :param dicts: 字典列表
    :return:
    """
    if (
        not dest_file_path
        or get_file_extension(dest_file_path).lower() != ".csv"
        or not dicts
    ):
        logger.warn(
            "dest_file_path is None, or dest_file is not `csv`, or dicts is None!"
        )
        return False

    dest_dir = os.path.dirname(dest_file_path)
    if not os.path.exists(dest_dir):
        create_directory(dest_dir)

    with open(dest_file_path, "w", encoding="utf-8-sig") as f:
        fieldnames = dicts[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in dicts:
            writer.writerow(row)

    return os.path.exists(dest_file_path)
