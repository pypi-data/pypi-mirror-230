# coding: utf-8
"""
    assetic.config  (config.py)
    Configure assetic_qgis
"""


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


@singleton
class Config(object):
    """
    class to initialise
    """
    def __init__(self):
        """
        Constructor of the class.
        """
        self.asseticsdk = None
        self.layerconfig = None
        self.loglevel = None
        self.logfile = None
        self.commontools = None
