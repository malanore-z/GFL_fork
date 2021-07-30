

from gfl.utils import ZipUtils


if __name__ == "__main__":
    data = ZipUtils.get_compress_data("__init__.py", "")
    ZipUtils.extract_data(data, "t2")
