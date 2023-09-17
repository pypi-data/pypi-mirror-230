from pathlib import Path

from .SHHSAnnotationLoader import SHHSAnnotationLoader
from pyPhasesRecordloader.recordLoaders.EDFRecordLoader import EDFRecordLoader
from pyPhasesRecordloader.recordLoaders.CSVMetaLoader import CSVMetaLoader


class RecordLoaderSHHS(EDFRecordLoader):
    def __init__(
        self,
        filePath,
        targetSignals,
        targetSignalTypes=[],
        optionalSignals=[],
        combineChannels=[],
    ) -> None:
        super().__init__(
            filePath,
            targetSignals,
            targetSignalTypes=targetSignalTypes,
            optionalSignals=optionalSignals,
            combineChannels=combineChannels,
        )

        self.exportsEventArray = True

    def isVisit1(self, recordName):
        return recordName[:5] == "shhs1"
    
    def getVisit(self, recordName):
        return 1 if self.isVisit1(recordName) else 2
    
    def getFileBasePath(self, recrdId):
        return self.filePath

    def getFilePathSignal(self, recordId):
        visit = self.getVisit(recordId)
        return f"{self.getFileBasePath(recordId)}/polysomnography/edfs/shhs{visit}/{recordId}.edf"

    def getFilePathAnnotation(self, recordId):
        visit = self.getVisit(recordId)
        return f"{self.getFileBasePath(recordId)}/polysomnography/annotations-events-nsrr/shhs{visit}/{recordId}-nsrr.xml"

    def existAnnotation(self, recordId):
        return Path(self.getFilePathAnnotation(recordId)).exists()

    def exist(self, recordId):
        return Path(self.getFilePathAnnotation(recordId)).exists() & Path(self.getFilePathSignal(recordId)).exists()

    def loadAnnotation(self, recordId, fileName, valueMap=None):
        filePath = self.getFilePathAnnotation(recordId)
        annotationLoader = SHHSAnnotationLoader.load(filePath, valueMap, self.annotationFrequency)

        return annotationLoader.events

    def getEventList(self, recordName, targetFrequency=1):
        metaXML = self.getFilePathAnnotation(recordName)
        xmlLoader = SHHSAnnotationLoader()

        eventArray = xmlLoader.loadAnnotation(metaXML)
        self.lightOff = xmlLoader.lightOff
        self.lightOn = xmlLoader.lightOn

        if targetFrequency != 1:
            eventArray = self.updateFrequencyForEventList(eventArray, targetFrequency)

        return eventArray

    def getMetaData(self, recordName, loadMetadataFromCSV=True):
        metaData = super().getMetaData(recordName)
        metaData["recordId"] = recordName
        if loadMetadataFromCSV:
            relevantRows = {
                "gender": lambda row: "male" if row["gender"] == 1 else "female",
                "age": "age_s1",
                "bmi": "bmi_s1",
                "tst": "slptime",
                "sLatency": "slp_lat",
                "rLatency": "rem_lat1",
                "waso": "WASO",
                "sEfficiency": "slp_eff",
                "indexArousal": "ai_all",
                # countArousal
                "ArREMBP": "ArREMBP",
                "ArREMOP": "ArREMOP",
                "ArNREMBP": "ArNREMBP",
                "ArNREMOP": "ArNREMOP",
                "ahi": "ahi_a0h4a",
                "bp_diastolic": "DiasBP",
                "bp_systolic": "SystBP",
                "race": "race", 
                # % N1, N2, N3, R
                # therapy / diagnostics
                # Diagnosis
                # PLMSI
                # PLMSIArI
            }
            # ArREMBP + ArREMOP + ArNREMBP + ArNREMOP
            visit = self.getVisit(recordName)
            csvLoader = CSVMetaLoader(
                f"{self.filePath}/datasets/shhs{visit}-dataset-0.15.0.csv", idColumn="nsrrid", relevantRows=relevantRows
            )
            csvMetaData = csvLoader.getMetaData(int(recordName[6:]))
            metaData.update(csvMetaData)

            metaData["countArousal"] = metaData["ArREMBP"] + metaData["ArREMOP"] + metaData["ArNREMBP"] + metaData["ArNREMOP"]

        return metaData
