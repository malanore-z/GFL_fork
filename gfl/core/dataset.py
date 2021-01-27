
from gfl.utils.po_utils import PlainObject


class Dataset(PlainObject):

    dataset_id = (int, )
    owner = (str, )
    description = (str, )
