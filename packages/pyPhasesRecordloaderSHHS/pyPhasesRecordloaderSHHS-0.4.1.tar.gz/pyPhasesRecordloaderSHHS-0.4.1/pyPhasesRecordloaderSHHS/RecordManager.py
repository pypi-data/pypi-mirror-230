from teleschlafmedizin.model.PSGSignal import PSGSignal
from teleschlafmedizin.model.Annotation import Annotation
from teleschlafmedizin.model.recordManager.RecordMeta import (
    Channel,
    Record,
    RecordAnnotation,
    RecordChannel,
)
from pyPhases.util.Logger import classLogger
from teleschlafmedizin.model.util.DynamicModule import DynamicModule
from . import recordManager as recordManagerPath


class ParseError(Exception):
    pass


class AnnotationException(Exception):
    path = []
    name = ""

    def __init__(self, path):
        self.path = path
        self.name = path[-1]
        super().__init__(self.getMessage())


class AnnotationNotFound(AnnotationException):
    def getMessage(self):
        return "Annotation was not found in the XML file: %s" % (self.path + [self.name])


class AnnotationInvalid(AnnotationException):
    def getMessage(self):
        return "Annotation is invalid: %s" % (self.path)


class ChannelsNotPresent(Exception):
    channels = []

    def __init__(self, channels, recordid="Unknown"):
        msg = "Channels of record %s where not present: %s" % (recordid, channels)
        super().__init__(msg)
        self.channels = channels


@classLogger
class RecordLoader:
    recordLoader = DynamicModule(recordManagerPath)

    def __init__(
        self,
        filePath="",
        targetFrequency=50,
        targetSignals=[],
        targetSignalTypes=[],
        optionalSignals=[],
    ) -> None:
        self.filePath = filePath
        self.targetFrequency = targetFrequency
        self.optionalSignals = optionalSignals
        self.targetSignals = targetSignals
        self.targetSignalTypes = targetSignalTypes
        # lightOff and lightOn are in seconds !
        self.lightOff = 0
        self.lightOn = None
        self.classificationConfig = {}
        self.exportsEventArray = False
        self.firstSleep = None
        self.lastSleep = None
        self.signalTypeDict = dict(zip(self.targetSignals, self.targetSignalTypes))
        self.useDigitalSignals = False

    def delete(self, recordName):
        pass

    def exist(self, recordName):
        pass

    def loadRecord(self, recordName):
        pass

    def getSignal(self, recordName) -> PSGSignal:
        pass

    def loadAnnotation(self, recordName):
        pass

    def getEventList(self, recordName):
        pass

    def existAnnotation(self, recordId):
        """Check if an annotation exist for a given recordId.

        Returns:
            boolean: annotation exist
        """
        return False

    @staticmethod
    def get() -> "RecordLoader":
        return RecordLoader.recordLoader.get()

    def fillRecordFromPSGSignal(self, record: Record, psgSignal: PSGSignal):

        record.recordName = psgSignal.recordId

        for signal in psgSignal.signals:
            signal.typeStr = self.getSignalTypeStrFromDict(signal.name)
        psgSignal.checkPSGQuality()

        for signal in psgSignal.signals:
            channel = Channel()
            recordChannel = RecordChannel()

            channel.name = signal.name
            channel.dimension = signal.dimension
            channel.min = signal.physicalMin
            channel.max = signal.physicalMax
            recordChannel.transducer = signal.transducer
            recordChannel.frequency = signal.frequency
            recordChannel.prefilter = signal.prefilter
            recordChannel.quality = signal.quality

            recordChannel.Channel = channel
            record.recordChannels.append(recordChannel)
        return record

    def getSignalTypeStrFromDict(self, signalName):
        if self.signalTypeDict == {}:
            self.signalTypeDict = dict(zip(self.targetSignals, self.targetSignalTypes))
        if signalName in self.signalTypeDict:
            signalTypeStr = self.signalTypeDict[signalName]
        else:
            self.logError("Signal '%s' had no type when initilizing the RecordLoader" % str(signalName))
            signalTypeStr = "unknown"
        return signalTypeStr


class RecordWriter:
    recordWriter = DynamicModule(recordManagerPath)
    record: Record = None

    def writerRecord(recordName):
        pass

    def writeAnnotation(self, annotation: Annotation):
        pass

    def writeDataAnnotation(self, dataAnnotation: RecordAnnotation):
        """Writes a RecordAnnotationannotation to the Record

        Args:
            dataAnnotation (Annotation): RecordAnnotation with events and an Annotation with name

        """
        a = self.annotation.fromDataAnnotation(dataAnnotation)
        return self.writeAnnotation(a)

    @staticmethod
    def get() -> "RecordWriter":
        return RecordWriter.recordWriter.get()


class RecordManager:
    @staticmethod
    def getReader() -> RecordLoader:
        return RecordLoader.get()

    def getWriter() -> RecordWriter:
        return RecordWriter.get()
