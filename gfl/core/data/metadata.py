from gfl.utils.po_utils import PlainObject


class Metadata(PlainObject):

    id = (str, )
    owner = (str, )
    create_time = (int, )
    content = (str, )


class JobMetadata(Metadata):

    pass


class DatasetMetadata(Metadata):

    pass
