import os
from pathlib import PurePath
from typing import NoReturn, Union
from zipfile import ZipFile, ZIP_DEFLATED


class ZipUtils(object):

    @classmethod
    def compress(cls, src_paths: Union[str, list], dst_zip_file, basename=None) -> NoReturn:
        """
        将src_paths指向的文件压缩成zip格式， 保存到dst_zip_file中。
        :param src_paths: 带压缩的文件或文件夹目录， 接受多个文件或文件夹以列表形式传入
        :param dst_zip_file: 类文件对象或文件路径，用于存储压缩后的数据
        :param basename: zip文件列表的根目录
        """
        if type(src_paths) not in [list, tuple, set]:
            src_paths = (src_paths, )
        if basename is None:
            basename = cls.__detect_basename(src_paths)
        if isinstance(dst_zip_file, str) and os.path.isdir(dst_zip_file):
            zip_filename = basename + ".zip"
            dst_zip_file = PurePath(dst_zip_file, zip_filename).as_posix()
        zip_file = ZipFile(dst_zip_file, "w", ZIP_DEFLATED)
        for p in src_paths:
            cls.__add_file(zip_file, basename, p)
        zip_file.close()

    @classmethod
    def extract(cls, src_zip_file, dst_path: str) -> NoReturn:
        """
        将zip文件解压到指定目录
        :param src_zip_file: 待解压的类文件对象或文件路径
        :param dst_path: 解压到的目录
        """
        zip_file = ZipFile(src_zip_file, "r", ZIP_DEFLATED)
        zip_file.extractall(dst_path)
        zip_file.close()

    @classmethod
    def __add_file(cls, zip_file: ZipFile, basename, source):
        for filename in os.listdir(source):
            new_source = PurePath(source, filename).as_posix()
            new_basename = PurePath(basename, filename).as_posix()
            if os.path.isdir(new_source):
                cls.__add_file(zip_file, new_basename, new_source)
            else:
                zip_file.write(new_source, new_basename)

    @classmethod
    def __detect_basename(cls, src_paths):
        if len(src_paths) == 1:
            return os.path.basename(src_paths[0])
        else:
            parent_dirname = os.path.dirname(src_paths[0])
            for p in src_paths[1:]:
                if parent_dirname != os.path.dirname(p):
                    return ""
            return os.path.basename(parent_dirname)
