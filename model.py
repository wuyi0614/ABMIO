import os
import sys
import numpy as np
import pandas as pd

try: module_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
except: module_path = "/Users/mario/Document/OneDrive/GitHub/"
sys.path.append(module_path)

from ABMIO.market import BaseMarket

import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BaseModel(BaseMarket):
	def __init__(self):
		super(BaseModel, self).__init__()

	def preload(self, shelve_object, iteration, label):
		super(BaseModel, self).preload(shelve_object, iteration, label)

	def sync(self, shelve_object, iteration, label):
		super(BaseModel, self).sync(shelve_object, iteration, label)

	def calibrate(self, syntax):
		super(BaseModel, self).calibrate(syntax)

	def recipe(self, *args):
		""" BaseMethod: pipe agents in the queue """
		super(BaseModel, self).recipe(*args)

	def function(self, *args, **kwargs):
		""" BaseMethod of BaseModel: takes in variables and function """
		self._variables = args
		self._function = kwargs
		logger.info("[{} Function] load [{}] functions and [{}] variables ".format(self.actor, len(self._function), len(self._variables)))

############ CES Model ############
class CES(BaseModel):
	def __init__(self):
		super(CES, self).__init__()

	@classmethod
	def synthetic_price(cls,alpha,price1,price2,delta):
		"""
		StaticMethod of CES Model
		Parameters (single value):
			- alpha: share param of commodities consumed
			- price1: Price of commodity 1
			- price2: Price of commodity 2
			- delta: elasticity of substitution
		Return:
			a synthetic Price of given parameters
		"""
		return (alpha * price1**(1-delta) + (1-alpha)* price2**(1-delta))**(1/(1-delta))

	def recipe(self, *args):
		super(CES, self).recipe(*args)

	def update(self, **kwargs):
		"""
		Update variables of Agent: sync varibales with Agents
		Parameters:
			- *kwargs: key-value ties are to be updated for agents in self.agents
		"""
		if not self.agents:
			logger.error("[{} Update] failed: no agent in queue, run self.recipe() first ".format(self.actor))
			return False
		for agent in self.agents:
			[agent.__setattr__(variable, value) for variable, value in kwargs.items()]
		logger.info("[{} Update] update [{}] agents with [{}] variables ".format(self.actor, len(self.agents), len(kwargs)))


	def solve(self, Alpha, Delta, Price, Intershare, Lambda, Output):
		"""
		Solve CES Model:
		Parameters:
			- Alpha: array of alpha values (the size matches that of producers)
			- Delta: array of elasticities (the size of alpha)
			- Price: array of prices (待修改)
			- Intershare (m): array of intermediate shares (default for three industries)
			- Lambda: single value of some operator for adjustment
			- Output: single value of one specific producer
		Return:
			- inputs: a dict of inputs elements, 
			example: `{'Fn1':Fn1,'Fn2':Fn2,'Fn3':Fn3,'Fn4':Fn4,'Fn5':Fn5,'ELE':ELE,
				'int1':int1,'int2':int2,'int3':int3,'L':L,'K':K}`
		"""
		# 原始数据中的指针从1开始，python从0开始，
		# transform np.ndarray back to list:
		if isinstance(Alpha, np.ndarray): Alpha = list(Alpha)
		if isinstance(Delta, np.ndarray): Delta = list(Delta)
		if isinstance(Intershare, np.ndarray): Intershare = list(Intershare)

		Alpha.insert(0, 99); Delta.insert(0, 99); Intershare.insert(0, 99)
		pr_K = Price[10] 
		pr_L = Price[11]
		pr_momg = self.synthetic_price(Alpha[1],Price[2],Price[3],Delta[1])
		pr_mcmo = self.synthetic_price(Alpha[2],Price[1],pr_momg,Delta[2])
		pr_oilcok = self.synthetic_price(Alpha[3],Price[4],Price[5],Delta[3])
		pr_Fn = self.synthetic_price(Alpha[4],pr_mcmo,pr_oilcok,Delta[4])
		pr_E = self.synthetic_price(Alpha[5],Price[6],pr_Fn,Delta[5])
		pr_KL = self.synthetic_price(Alpha[6],pr_K,pr_L,Delta[6])
		pr_KEL = self.synthetic_price(Alpha[7],pr_KL,pr_E/Lambda,Delta[7])
		pr_INT = Intershare[1] * Price[7] + Intershare[2] * Price[8] + Intershare[3] * Price[9]
		pr_x = self.synthetic_price(Alpha[8],pr_KEL,pr_INT,Delta[8])

		# input calculation
		KEL = Alpha[8] * (pr_x/pr_KEL)**(Delta[8]) * Output
		INT = (1-Alpha[8]) * (pr_x/pr_INT)**(Delta[8]) * Output
		KL = Alpha[7] * (pr_KEL/pr_KL)**(Delta[7]) * KEL
		E = Lambda**(Delta[7]-1) * (1-Alpha[7]) * (pr_KEL/pr_E)**(Delta[7]) * KEL
		K = Alpha[6] * (pr_KL/pr_K)**(Delta[6]) * KL
		L = (1-Alpha[6]) * (pr_KL/pr_L)**(Delta[6]) * KL
		ELE = Alpha[5] * (pr_E/Price[6])**(Delta[5]) * E
		Fn = (1-Alpha[5]) * (pr_E/pr_Fn)**(Delta[5]) * E
		Z2 = Alpha[4] * (pr_Fn/pr_mcmo)**(Delta[4]) * Fn
		Z3 = (1-Alpha[4]) * (pr_Fn/pr_mcmo)**(Delta[4]) * Fn
		Fn4 = Alpha[3] * (pr_oilcok/Price[4])**(Delta[3]) * Z3
		Fn5 = (1-Alpha[3]) * (pr_oilcok/Price[5])**(Delta[3]) * Z3
		Fn1 = Alpha[2] * (pr_mcmo/Price[1])**(Delta[2]) * Z2
		Z1 = (1-Alpha[2]) * (pr_mcmo/Price[1])**(Delta[2]) * Z2
		Fn2 = Alpha[1] * (pr_momg/Price[2])**(Delta[1]) * Z1
		Fn3 = (1-Alpha[1]) * (pr_momg/Price[3])**(Delta[1]) * Z1
		int1 = INT * Intershare[1]
		int2 = INT * Intershare[2]
		int3 = INT * Intershare[3]	

		# outcome:
		res = {'Fn1':Fn1,'Fn2':Fn2,'Fn3':Fn3,'Fn4':Fn4,'Fn5':Fn5,'ELE':ELE,
				'int1':int1,'int2':int2,'int3':int3,'L':L,'K':K}
		return res
    

############ IO Model ############
class IO(BaseModel):
	""" IO object: only accepts pandas.DataFrame object """
	def __init__(self):
		super(IO, self).__init__()
		self.__setattr__("{}_econ_rawtable".format(self._actor, pd.DataFrame()))
		self.__setattr__("{}_econ_intertable".format(self._actor, pd.DataFrame()))

	def preload(self, shelve_object, iteration, label):
		super(IO, self).preload(shelve_object, iteration, label)

	def sync(self, shelve_object, iteration, label):
		super(IO, self).sync(shelve_object, iteration, label)

	def set_tablenames(self, table, **kwargs):
		rownames = kwargs.get("rownames","")
		colnames = kwargs.get("colnames","")
		if self.__getattribute__(table).empty:
			_table = self.__getattribute__(table)
			_table.index = rownames
			_table.columns = colnames
		else:
			logger.error("[{} Names] empty table, load from DB or pipe a new one.")

	def set_tables(self, **kwargs):
		"""
		Set tables by piping `intertable` or `rawtable` into the object
		Parameters:
			- **kwargs: accepts <io>_econ_rawtable or <io>_econ_intertable and corresponding `pandas.DataFrame`
		"""
		for table, df in kwargs.items():
			if hasattr(self, table):
				self.__setattr__(table, df)
				logger.info("[{} Tables] set [{}] with DataFrame ({})".format(self.actor, table, df.shape))
			else:
				logger.error("[{} Tables] invalid tablename [{}], please check ".format(self.actor, table))

	@staticmethod
	def compress(dataframe, label, *indice):
		"""
		StaticMethod: compress iotable by specifying `indice`
		Parameters:
			- label: new label for the compressed dimension
			- *indice: the list of indice that is to be compressed 
		Return:
		Compressed `DataFrame` table with compressed column and row at the bottom 
		"""
		array = dataframe.to_numpy()
		# row operations:
		rowsum = array[indice, :].sum(axis=0)
		array = np.delete(array, indice, axis=0)  # delete rows
		array = np.row_stack((array, rowsum))
		# column operations:
		colsum = array[:, indice].sum(axis=1)
		array = np.delete(array, indice, axis=1)  # delete rows
		array = np.column_stack((array, colsum))
		# reset the colnames and rownames:
		rownames = np.array(dataframe.index)
		colnames = np.array(dataframe.columns)
		rownames = np.delete(rownames, indice, axis=0)
		colnames = np.delete(colnames, indice, axis=0)
		# update names:
		rownames = np.append(rownames, label)
		colnames = np.append(colnames, label)
		# restore dataframe:
		table = pd.DataFrame(array)
		table.index = rownames; table.columns = colnames
		return table


