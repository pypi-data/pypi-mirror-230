import pyedflib

from ..RecordSignal import RecordSignal
from ..Signal import Signal
from ..RecordLoader import ChannelsNotPresent, ParseError, RecordLoader


class EDFRecordLoader(RecordLoader):
    def __init__(self, filePath, targetSignals, targetSignalTypes, optionalSignals=None, combineChannels=None) -> None:
        super().__init__(
            filePath=filePath,
            targetSignals=targetSignals,
            targetSignalTypes=targetSignalTypes,
            optionalSignals=optionalSignals,
            combineChannels=combineChannels,
        )
        self.annotations = []
        self.channelMap = {}

    def getSignal(self, recordName):
        edfFile = self.getFilePathSignal(recordName)
        signal = self.loadSignal(edfFile)
        signal.recordId = recordName
        return signal
    
    def getSignalHeaders(self, recordName):
        edfFile = self.getFilePathSignal(recordName)
        return self.loadSignalHeaders(edfFile)

    def getAnnotationTimeByName(self, name):
        for time, n in zip(self.annotations[0], self.annotations[2]):
            if n == name:
                return time

        return None

    def loadSignal(self, edfFile, annotations=False):
        recordSignal = RecordSignal()
        headers, f = self.loadSignalHeadersAndHandle(edfFile)
        
        if f.annotations_in_file > 0:
            self.annotations = f.readAnnotations()
        
        for header in headers:
            signalName = header["signalName"]
            typeStr = header["type"]
            index = header["index"]
            
            signalArray = f.readSignal(index, digital=self.useDigitalSignals)
            
            signal = Signal(signalName, signalArray, frequency=header["sample_rate"])
            signal.typeStr = typeStr
            signal.setSignalTypeFromTypeStr()
            signal.isDigital = self.useDigitalSignals
            signal.digitalMin = header["digital_min"]
            signal.digitalMax = header["digital_max"]
            signal.physicalMin = header["physical_min"]
            signal.physicalMax = header["physical_max"]
            signal.dimension = header["dimension"]
            signal.sourceIndex = index
            signal.prefilter = header["prefilter"]
            recordSignal.addSignal(signal, signalName)
            
        return recordSignal
    
    def loadSignalHeaders(self, edfFile, annotations=False):
        return self.loadSignalHeadersAndHandle(edfFile, annotations)[0]
    
    def loadSignalHeadersAndHandle(self, edfFile, annotations=False):
        try:
            self.logDebug("Read EDF Header %s" % edfFile)
            f = pyedflib.EdfReader(edfFile)
        except Exception as ex:
            raise ParseError("Failed to read EDF File %s: %s" % (edfFile, str(ex)))

        n = f.signals_in_file
        targetSignals = self.targetSignals if annotations == False else self.annotationSignal
        if len(targetSignals) == 0:
            raise Exception(
                "The RecordLoader has no target signals to extract, please specificy 'sourceSignals' with the name of the channels"
            )
            
        expectedSignals = len(targetSignals)
        addedSignals = []
        ignoredChannels = []
        signalHeaders = []
        for i in range(n):
            header = f.getSignalHeader(i)
            channelLabel = header["label"]
            signalName = self.chanelNameAliasMap[channelLabel] if channelLabel in self.chanelNameAliasMap else channelLabel
            if signalName in targetSignals:
                header["signalName"] = signalName
                header["type"] = self.getSignalTypeStrFromDict(signalName)
                header["index"] = i
                self.channelMap[signalName] = i
                signalHeaders.append(header)
                addedSignals.append(signalName)
            else:
                ignoredChannels.append(signalName)

        self.log("Added %i signals, ignored: %s" % (len(addedSignals), ignoredChannels))
        if len(addedSignals) < expectedSignals:
            missingchannels = set(self.targetSignals) - set(addedSignals) - set(self.optionalSignals)
            if len(missingchannels) > 0:
                raise ChannelsNotPresent(missingchannels, edfFile)

        return signalHeaders, f

    def getMetaData(self, recordName):
        edfFile = self.getFilePathSignal(recordName)
        f = pyedflib.EdfReader(edfFile)
        return {
            "recordId": recordName,
            "patientName": f.getPatientName(),
            "patientCode": f.getPatientCode(),
            "patientAdd": f.getPatientAdditional(),
            "start": f.getStartdatetime(),
            "technician": f.getTechnician(),
            "dataCount": f.datarecords_in_file,
        }

