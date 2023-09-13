from pyPhasesML.datapipes.DataPipe import DataPipe


class RecordMap(DataPipe):
    def __init__(self, dataset: DataPipe, mapping):
        self.dataset = dataset
        self.mapping = mapping
        self.currentIndex = 0

    def __len__(self):
        return len(self.mapping)

    def __getitem__(self, index):
        return self.dataset[self.mapping[index]]
