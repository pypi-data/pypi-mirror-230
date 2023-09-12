# coding: utf-8
"""
    Initialise package
"""

import logging

from assetic.tools.shared import InitialiseBase

from assetic_qgis import __version__


class Initialise(InitialiseBase):
    def __init__(self, config):
        # initialise obejct here with all of the values we need
        super().__init__(__version__, config=config)

        # Get the assetic sdk file logger
        assetic_sdk_handle = None
        for sdk_handle in config.asseticsdk.logger.handlers:
            if isinstance(sdk_handle, logging.handlers.RotatingFileHandler):
                assetic_sdk_handle = sdk_handle

                break

        # when the assetic-qgis package is initiated a logger is created
        # to catch any issues that occur before this config instance is
        # initialised (%APPDATA%/addin.log)
        # Now we have a log file defined in the config we can remove
        # that handler and attach the sdk handler
        qgis_logger = logging.getLogger(__name__).parent
        for handle in qgis_logger.handlers:
            if type(handle) == logging.FileHandler:
                if assetic_sdk_handle:
                    qgis_logger.removeHandler(handle)
                    # now attach the handler defined in the xml config file
                    qgis_logger.addHandler(assetic_sdk_handle)
                    break
                elif config.logfile:
                    # log file in XML but not initiating script so use that
                    # as the logger for assetic_esri logger
                    log_formatter = handle.formatter
                    qgis_logger.removeHandler(handle)
                    new_handle = logging.FileHandler(config.logfile)
                    new_handle.formatter = log_formatter
                    qgis_logger.addHandler(new_handle)
