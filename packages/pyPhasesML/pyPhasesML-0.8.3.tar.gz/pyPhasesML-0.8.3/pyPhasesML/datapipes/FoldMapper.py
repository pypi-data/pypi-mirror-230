from .RecordMap import RecordMap


class FoldMapper:
    def __init__(self, datasetLength, folds, validationPostion):
        self.folds = folds
        self.validationPostion = validationPostion

        records = range(datasetLength)
        validataionSize = len(records) // self.folds
        if validataionSize == 0:
            raise Exception("The dataset is too small for the given number of folds")
        self.validationRecords = records[
            self.validationPostion * validataionSize : (self.validationPostion + 1) * validataionSize
        ]
        self.trainingsRecords = [record for record in records if record not in self.validationRecords]

    def getTraining(self, dataset):
        return RecordMap(dataset, self.trainingsRecords)

    def getValidation(self, dataset):
        return RecordMap(dataset, self.validationRecords)

    def getTrainingMap(self):
        return self.trainingsRecords

    def getValidationMap(self):
        return self.validationRecords
