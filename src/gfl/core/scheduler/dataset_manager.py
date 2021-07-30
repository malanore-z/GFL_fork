
import gfl.core.lfs as lfs
from gfl.core.data import Dataset
from gfl.core.scheduler.manager import Manager
from gfl.net import NetBroadcast


class DatasetManager(Manager):

    @classmethod
    def submit_dataset(cls, dataset: Dataset):
        lfs.save_dataset(dataset)
        dataset_file = lfs.load_dataset_zip(dataset.dataset_id)
        NetBroadcast.broadcast_dataset(dataset.dataset_id, dataset_file)
