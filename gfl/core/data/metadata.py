__all__ = [
    "DatasetMetadata",
    "JobMetadata"
]

from gfl.utils.po_utils import PlainObject


class Metadata(PlainObject):

    id: str = None
    owner: str = None
    create_time: int
    content: str


class DatasetMetadata(Metadata):

    pass


class JobMetadata(Metadata):

    pass
