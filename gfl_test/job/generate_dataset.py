from gfl.core.entity.config import DatasetConfig
from gfl.core.manager import DatasetManager

import gfl_test.dataset as gfl_dataset


if __name__ == "__main__":
    dataset_config = DatasetConfig().with_dataset("mnist_dataset").with_val_rate(0.3)
    id = DatasetManager.generate_dataset(gfl_dataset, dataset_config)
    print(id)
    pass