# coding: utf-8
"""
    Initialise package
"""

import assetic
import logging
from assetic.tools.shared.initialise_base import InitialiseBase

from .__version__ import __version__
from .qgis_config import QgisConfig
from .settings.assetic_qgis_config import LayerConfig
from .tools.qgis_messager import QgisMessager


class Initialise(InitialiseBase):
    def __init__(self, feedback, configfile=None, inifile=None, logfile=None
                 , loglevelname=None):
        """
        Constructor of the class.
        :Param configfile: the name of the XML config file with ESRI to
        Assetic field mappings. If none then will look in the users
        appdata\Assetic folder for arcmap_edit_config.xml
        :Param inifile: the file name (including path) of the ini file
        (host, username, api_key).
        If none then will look in local folder for assetic.ini
        ,else look in environment variables for asseticSDKhost
        , asseticSDKusername,asseticSDKapi_key
        :Param logfile: the file name (including path) of the log file.
        If None then no logfile will be created
        :Param loglevelname: set as a valid logging level description
        e.g. INFO
        """
        super(InitialiseBase, self).__init__()

        config = QgisConfig()
        # initialise common tools so can use messaging method
        config.messager = QgisMessager(feedback)

        # read xml config file if one was passed in
        if configfile is not None:
            config.layerconfig = LayerConfig(configfile)

        warn_log_level_conflict = False
        # check of log level is defined in config file and use that
        if loglevelname and config.layerconfig and config.layerconfig.loglevel:
            if loglevelname != config.layerconfig.loglevel:
                warn_log_level_conflict = True
                loglevelname = config.layerconfig.loglevel
        elif config.layerconfig and config.layerconfig.loglevel:
            loglevelname = config.layerconfig.loglevel

        warn_log_file_conflict = False
        # check of log file name defined in config file and use that
        if logfile and config.layerconfig and config.layerconfig.logfile:
            if logfile != config.layerconfig.logfile:
                warn_log_file_conflict = True
                logfile = config.layerconfig.logfile
        elif not logfile and config.layerconfig and config.layerconfig.logfile:
            logfile = config.layerconfig.logfile

        # initialise the Assetic sdk library
        config.asseticsdk = assetic.AsseticSDK(inifile, logfile, loglevelname)
        msg = "Initiated Assetic-QGIS. Version {0}".format(__version__)
        config.asseticsdk.logger.info(msg)
        if warn_log_file_conflict:
            config.asseticsdk.logger.warn(
                "Differing logfile names defined in configuration xml and "
                "passed in parameter.  Definition in configuration xml will "
                "be used")
        if warn_log_level_conflict:
            config.asseticsdk.logger.warn(
                "Differing log levels defined in configuration xml and "
                "passed in parameter.  Definition in configuration xml will "
                "be used")
        assetic_sdk_handle = None
        for sdk_handle in config.asseticsdk.logger.handlers:
            if isinstance(sdk_handle, logging.handlers.RotatingFileHandler):
                assetic_sdk_handle = sdk_handle
                break
        if logfile and not assetic_sdk_handle:
            assetic_sdk_handle = logging.FileHandler(logfile)
        elif not logfile:
            assetic_sdk_handle = logging.StreamHandler()

        # when the assetic-qgis package is initiated a logger is created
        # to catch any issues that occur before this config instance is
        # initialised
        # Now we have a log file defined in the config we can remove
        # that handler and attach the sdk handler
        assetic_qgis_logger = logging.getLogger(__name__).parent
        for handle in assetic_qgis_logger.handlers:
            if isinstance(handle, logging.FileHandler):
                assetic_qgis_logger.removeHandler(handle)
                # now attach the handler defined in the xml config file
                assetic_qgis_logger.addHandler(assetic_sdk_handle)
                break

        min_version = "2019.13.2.0"
        try:
            assetic_version = assetic.__version__.__version__.split(".")
        except Exception as ex:
            config.asseticsdk.logger.info("Unable to determine version of"
                                          " Assetic python package: {0}"
                                          .format(ex))
        else:
            if assetic_version >= min_version.split("."):
                pass
            else:
                # version may be too old.  Issue warning
                config.asseticsdk.logger.warning(
                    "Current version of assetic python package is too old."
                    " Version is: {0}, expecting minimum of {1}".format(
                        assetic.__version__.__version__), min_version)
