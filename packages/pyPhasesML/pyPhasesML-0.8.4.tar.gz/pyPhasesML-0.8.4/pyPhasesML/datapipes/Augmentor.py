
from pyPhasesML.datapipes import DataPipe

from ..DataAugmentation import DataAugmentation


class Augmentor:
    def __init__(self, datapipe: DataPipe, augmentation: DataAugmentation, config) -> None:
        self.datapipe = datapipe
        self.augmentation = augmentation
        self.config = config

    def __getitem__(self, index):
        return self.augmentation(self.datapipe[index], self.config, index)

    def __len__(self):
        return len(self.datapipe)

