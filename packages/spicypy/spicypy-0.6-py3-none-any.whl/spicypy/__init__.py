"""
| Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>
| Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>
"""

import logging as log
import sys
from importlib import metadata

from spicypy import control, signal

try:
    __version__ = metadata.version(__name__)
except metadata.PackageNotFoundError:
    __version__ = "unknown"
    log.warning("Version not known, importlib.metadata is not working correctly.")

__all__ = ["control", "signal"]
