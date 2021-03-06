
from gfl.core.data.config import DatasetConfig
from gfl.core.data.metadata import DatasetMetadata


class Dataset(object):

    def __init__(self, *,
                 dataset_id: str = None,
                 metadata: DatasetMetadata = None,
                 dataset_config: DatasetConfig = None):
        super(Dataset, self).__init__()
        self.module = None
        self.dataset_id = dataset_id
        self.metadata = metadata
        self.dataset_config = dataset_config
