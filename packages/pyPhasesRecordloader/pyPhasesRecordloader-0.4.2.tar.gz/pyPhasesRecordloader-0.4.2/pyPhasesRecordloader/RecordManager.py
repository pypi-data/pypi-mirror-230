from .util.DynamicModule import DynamicModule
from . import recordLoaders as recordManagerPath


class RecordWriter:
    recordWriter = DynamicModule(recordManagerPath)
    record = None

    def writerRecord(recordName):
        pass

    def writeAnnotation(self, annotation):
        pass

    def writeDataAnnotation(self, dataAnnotation):
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
