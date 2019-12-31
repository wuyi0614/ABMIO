# -*- utf-8 -*-
"""
@author:
"""
import os

import sys
try: module_path = os.path.abspath(os.path.dirname(__file__))
except: module_path = "/Users/mario/Desktop/"
sys.path.append(module_path)
from ABM.parameter import *

import pandas as pd
import numpy as np

import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class IOTableError(Exception):
	pass

class IOModule(object):
	""" IO object: only accepts pandas.DataFrame object """
	def __init__(self):
		self.io = pd.DataFrame()
		self.io_metadata = []  # rowname, colnames
		# //todo
		logger.info("[{} Initialise] model starts... ".format())


	def _set_tablenames(self,**kwargs):
		rownames = kwargs.get("rownames","")
		colnames = kwargs.get("colnames","")
		if self.io.emtpy:
			raise IOTableError("IO table missing, call .getIO() ")
		else:
			try:
				self.io.index = rownames
				self.io.columns = colnames
			except:
				logger.error([])


	@staticmethod
	def processIO(**kwargs):
		""" .processIO only helps with intermediate IO Table
		KeywordArguments:
			- inter_table: notably, colnumber equals rownumber.
		"""
		io_table = pd.DataFrame()
		inter_table = kwargs.get("inter_table","")
		if isinstance(inter_table,(list,np.ndarray,pd.DataFrame)):
			if not isinstance(inter_table,pd.DataFrame):
				io_table = pd.DataFrame(inter_table)
			else:
				io_table = inter_table
			# verify the size of table:
			_shape = io_table.shape
			if _shape[0] == _shape[1]:
				pass
			else:
				raise IOTableError("invaild size of `inter_table`: (%s:%s)"%_shape)
		else:
			raise IOTableError("invaild `inter_table` type, accept `np.ndarray`, `pd.DataFrame`, `list` ")
		return io_table


	def saveIO(self):
		if not self.io.empty:
			self.she.save("io_table",self.io)
			logger.info("[IOModule Save] save IO Table at [{}/{}] ".format(self.shelve_path,self.shelve_name))
		else:
			raise IOTableError("IO Table missing, call .processIO first ")


	@staticmethod  # 类方法: 在不启动IOModule时，即可以使用以下函数
	def getIO(shelve_path,shelve_name):
		she = Shelve(path=shelve_path,name=shelve_name)
		_io = she.query("io_table")
		if not _io:
			raise AgentError("no IO Table in Shelve [%s] "%(shelve_path + shelve_name))
		else:
			return _io


	@staticmethod
	def bindIO(targets=[]):
		pass


	def updateIO(self,):
		pass