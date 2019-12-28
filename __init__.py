"""
@Theme: __init__ module
@Author: Juli
@CreatDate: 2019-12-09
"""
import os

import sys
try: module_path = os.path.abspath(os.path.dirname(__file__))
except: module_path = "/Users/mario/Desktop/"
sys.path.append(module_path)

from ABM.parameter import Shelve

import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

