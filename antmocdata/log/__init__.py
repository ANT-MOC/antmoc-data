"""Package antmocdata.log.

This package contains classes and functions for log file analysis.

Authors: An Wang, USTB (wangan.cs@gmail.com)

Data: 2020/11/16

"""

__all__ = ["fields"]

from .options import LogOptions as Options
from .extract import TinyExtractor
from .data import *
