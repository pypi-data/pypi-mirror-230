# coding: utf-8

"""
    Assetic ESRI Integration API

    OpenAPI spec version: v2
"""

from __future__ import absolute_import

import logging
import os

import sys

from .__version__ import __version__
from .initialise import Initialise

from .addin_util.mi_addin_layout_customframe_util import LayoutCustomFrameUtil
from .addin_util.mi_addin_resourceManager import StringResourceManager
from .addin_util.mi_addin_util import AddinUtil
from .addin_util.mi_common_util import CommonUtil
from .addin_util.mi_user_interaction import UserInteraction
from .tools.mapinfo_config import MapInfoConfig
from .tools.mapinfo_layertools import MapInfoLayerTools

# setup logging with some hardcoded settings so we can trap any initialisation
# errors which can be more difficult to trap when running in ArcGIS
logger = logging.getLogger(__name__)
appdata = os.environ.get("APPDATA")
logfile = os.path.abspath(appdata + r"\Assetic\addin.log")
if not os.path.isdir(os.path.abspath(appdata + r"\Assetic")):
    try:
        os.mkdir(os.path.abspath(appdata + r"\Assetic"))
    except Exception:
        # just put iti in appdata
        logfile = os.path.abspath(appdata + r"\addin.log")

f_handler = logging.FileHandler(logfile)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
f_handler.setFormatter(formatter)
logger.addHandler(f_handler)
logger.setLevel(logging.INFO)


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    If an exception is uncaught it isn't written to the log, so capture the
    exception here and write to the log.  It will also write to stderr
    :param exc_type: exception type
    :param exc_value: exception
    :param exc_traceback: traceback
    """
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    if not issubclass(exc_type, KeyboardInterrupt):
        logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value,
                                            exc_traceback))


sys.excepthook = handle_uncaught_exception
config = MapInfoConfig()
