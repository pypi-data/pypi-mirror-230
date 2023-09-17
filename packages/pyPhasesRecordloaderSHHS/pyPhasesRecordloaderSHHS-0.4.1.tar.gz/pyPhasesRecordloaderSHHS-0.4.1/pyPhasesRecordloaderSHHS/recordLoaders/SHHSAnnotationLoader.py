from typing import List

from pyPhases.util.Logger import classLogger
from pyPhasesRecordloader import AnnotationInvalid, AnnotationNotFound, Event
from pyPhasesRecordloader.recordLoaders.XMLAnnotationLoader import XMLAnnotationLoader


@classLogger
class SHHSAnnotationLoader(XMLAnnotationLoader):
    stageMap = {
        "Wake|0": "W",
        "Stage 1 sleep|1": "N1",
        "Stage 2 sleep|2": "N2",
        "Stage 3 sleep|3": "N3",
        "Stage 4 sleep|4": "N3",
        "REM sleep|5": "R",
        # "Unsure|Unsure": "undefined",
        "Unscored|9": "undefined",
    }

    eventMap = {
        # "arousal_spontaneous", "arousal_plm", "", "arousal_bruxism", "arousal_noise"
        # "NasalSnore": "arousal_snore",
        # "CheyneStokesRespiration": "resp_cheynestokesbreath",
        "RERA|RERA": "arousal_rera",
        "Arousal|Arousal ()": "arousal",
        "ASDA arousal|Arousal (ASDA)": "arousal_asda",
        "Arousal resulting from Chin EMG|Arousal (CHESHIRE)": "arousal_chin",
        "Arousal|Arousal (STANDARD)": "arousal",
        # "LegMovement": "LegMovement",
    }

    eventMapApnea = {
        "Obstructive apnea|Obstructive Apnea": "resp_obstructiveapnea",
        "Central apnea|Central Apnea": "resp_centralapnea",
        "Hypopnea|Hypopnea": "resp_hypopnea",
        "Mixed apnea|Mixed Apnea": "resp_mixedapnea",
        # "SpO2 desaturation|SpO2 desaturation": "spo2_desaturation",
        # "SpO2 artifact|SpO2 artifact": "SpO2_artifact",
        # "Unsure|Unsure": "undefined",
    }

    eventMapSpO2 = {
        "SpO2 desaturation|SpO2 desaturation": "spo2_desaturation",
        "SpO2 artifact|SpO2 artifact": "SpO2_artifact",
    }

    # eventMapArtefacts = {
    #     "SpO2 artifact|SpO2 artifact": "SpO2_artifact",
    # }

    def getPath(self, xml, path):
        path = "./ScoredEvents/ScoredEvent" + path
        return xml.findall(path)

    def loadEvents(
        self,
        path,
        eventMap,
        durationChild="Duration",
        startChild="Start",
        typeChild="EventType",
        conceptChild="EventConcept",
        defaultState="ignore",
        minDuration=0,
        replaceName=None,
    ):
        tags = self.getPath(self.metaXML, path)
        if tags is None:
            raise AnnotationNotFound(path)

        events = []

        lastDefaultEvent = None
        for tag in tags:
            name = tag.find(conceptChild).text
            startValue = float(tag.find(startChild).text)
            if startValue is None:
                raise AnnotationInvalid(path + [startChild])

            startInSeconds = float(startValue)
            # if the name is in the eventMap it will be added to the annotations
            if name in eventMap:
                event = Event()
                event.start = startInSeconds
                event.manual = True
                eventName = replaceName(tag) if replaceName else eventMap[name]

                event.name = eventName

                if durationChild is not None:
                    # if there is a duration the event will be saved as as 2 events:
                    # startTime, "(eventName"
                    # endTime, "eventName)"
                    durationValue = float(tag.find(durationChild).text)
                    if durationValue is None:
                        raise AnnotationInvalid(path + [durationChild])

                    durationInSeconds = float(durationValue)
                    if durationInSeconds > minDuration:
                        event.duration = durationInSeconds
                        events.append(event)
                else:
                    # if its without a duration, it is considered a permanent state change
                    # that will persist until it is changed again
                    if lastDefaultEvent is not None:
                        lastDefaultEvent.duration = event.start - lastDefaultEvent.start
                    events.append(event)
                    lastDefaultEvent = event
            # else:
            #     self.logWarning("Event " + name + " not in EventMap.")

        if lastDefaultEvent is not None and self.lightOn is not None:
            lastDefaultEvent.duration = self.lightOn - lastDefaultEvent.start

        return events

    def loadAnnotation(self, xmlFile) -> List[Event]:
        self.loadXmlFile(xmlFile)

        allEvents = []
        allEvents += self.loadEvents(
            "[EventType='Stages|Stages']",
            self.stageMap,
        )
        allEvents += self.loadEvents(
            "[EventType='Arousals|Arousals']",
            self.eventMap,
        )

        allEvents += self.loadEvents(
            "[EventType='Respiratory|Respiratory']",
            self.eventMapApnea,
        )

        # allEvents += self.loadEvents(
        #     "[EventType='Respiratory|Respiratory']",
        #     self.eventMapSpO2,
        # )

        self.lightOff = 0
        self.lightOn = None

        return allEvents

    def fillRecord(self, record, xmlFile):
        pass
