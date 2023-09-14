
from assetic.tools.shared.messager_base import MessagerBase


class QGISMessager(MessagerBase):
    def __init__(self, feedback):
        super().__init__()
        self._feedback = feedback # this is a qgis object

    def new_message(self, msg, *args):
        try:
            self._feedback.pushInfo(msg)
            self.logger.debug(msg)
        except AttributeError:
            # feedback not setup
            print(msg)
            self.logger.info(msg)

    @property
    def is_cancelled(self):
        try:
            return self._feedback.isCanceled()
        except Exception as ex:
            # feedback not setup
            print("feedback error: {0}".format(str(ex)))
