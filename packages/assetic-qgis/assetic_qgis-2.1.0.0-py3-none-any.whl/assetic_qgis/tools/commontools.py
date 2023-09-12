import logging


class CommonTools(object):
    """
    Class of tools to support app
    """

    def __init__(self, feedback):
        self.logger = logging.getLogger(__name__)
        self._feedback = feedback

    @property
    def is_cancelled(self):
        return self._feedback.isCanceled()

    def new_message(self, message):
        """
        Push feedback message to QGis
        :param message: the message string for the user
        """
        try:
            self._feedback.pushInfo(message)
        except Exception as ex:
            # feedback not setup
            print("feedback error: {0}".format(str(ex)))
            self.logger.info(message)
