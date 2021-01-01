from io import BytesIO

from gfl.conf import GflConf
from gfl.utils import IpfsUtils, ZipUtils


def load_dir(dir):
    bytes_file = BytesIO()
    ZipUtils.compresss(dir, bytes_file, basename="")
    bytes_file.seek(0)
    zip_obj = bytes_file.read()
    zip_ipfs = None
    if GflConf.ipfs.enabled:
        zip_ipfs = IpfsUtils.put(zip_obj)
        zip_obj = None
    return zip_ipfs, zip_obj


def store_dir(dir, zip_ipfs, zip_obj):
    if zip_ipfs is not None:
        zip_obj = IpfsUtils.get(zip_ipfs)
    bytes_file = BytesIO(zip_obj)
    ZipUtils.extract(bytes_file, dir)
