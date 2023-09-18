# -*- coding: utf-8 -*-
import urllib3

from sctrader import exceptions
from sctrader.api import use, follower
from sctrader.log import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__version__ = "0.23.0"
__author__ = "shidenggui"
