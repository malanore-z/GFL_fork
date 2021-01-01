import os
from pathlib import PurePath
from zipfile import ZipFile, ZIP_DEFLATED


class ZipUtils(object):

    @classmethod
    def compresss(cls, src_path, dst_zip_file, basename=None):
        if basename is None:
            basename = os.path.basename(src_path)
        if isinstance(dst_zip_file, str) and os.path.isdir(dst_zip_file):
            zip_filename = os.path.basename(src_path)
            dst_zip_file = PurePath(dst_zip_file, zip_filename).as_posix()
        zip_file = ZipFile(dst_zip_file, "w", ZIP_DEFLATED)
        cls.__add_file(zip_file, basename, src_path)
        zip_file.close()

    @classmethod
    def extract(cls, src_zip_file, dst_path):
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
