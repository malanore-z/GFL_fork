from gfl.utils.po_utils import PlainObject


class Metadata(PlainObject):

    id: str = None
    owner: str = None
    create_time: int
    content: str


class JobMetadata(Metadata):

    pass


class DatasetMetadata(Metadata):

    pass
