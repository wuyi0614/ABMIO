"""
@Theme: Agents module
@Author: Juli
@CreatDate: 2019-12-09
"""

import os
import sys
import pandas as pd
import numpy as np

import sys
try: module_path = os.path.abspath(os.path.dirname(__file__))
except: module_path = "/Users/mario/Desktop/carbon_market_code/"
sys.path.append(module_path)

#from ABM.Parameter import Shelve
#from ABM.CES import CESModule

import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# import Agent.Producer
PATH = '/Users/juli/Desktop/Graduation_Project/carbon_trade/codes/ces_data/'

class AgentError(Exception):
	pass

__ALL__ = ["Producer","Government","Consumer"]


class Production(object):
	"""
	生产模块: 将定制后的厂商传入本模块，经过生产条件(模块)的加工后，更新厂商的经济属性
	Functions:
		- _recipe: 配置不同行业的厂商
		- produce: 生产函数，根据条件更新企业的产出: `.producer_output`
	"""
	def __init__(self):
		pass

	def _recipe(self,*args):
		""" 菜单: 放置厂商至生产环节 """
		if args:
			self.production_size = len(args)
			self.production_agents = {each.producer_sector:each for each in args}
			return True
		else:
			logger.error("empty producer queue, specify *args by producers ")
			return False


	def produce(self, *args, **kwargs):
		"""
		生产决策: 根据给定的生产决策函数 `_function` 更新厂商的经济变量 `args`, `kwargs` 给出不同产业部门的生产决策函数
		Parameter:
			- _function: produce function with arguments == args
			- *args: economic variables
			- **kwargs: production function for different sectors, if specify {"all":_function}, apply same function
		"""
		if kwargs: pass
		else:
			def _default(output, costs):
				output = np.random.normal(np.mean(output) * 1.1, np.mean(output)//10, len(output))
				costs = np.random.normal(np.mean(costs) * 1.1, np.mean(costs)//10, len(costs))
				return [output, costs]
			kwargs = {"all":_default}
			
		if args: pass
		else: args = ["producer_output","producer_econ_costs"]
		# update production variables:
		for sector, function in kwargs.items():
			if sector == "all":
				for psector, producer in self.production_agents.items():
					params = [producer.__getattribute__(key) for key in args]
					# call production function:
					print(params)
					changes = function(*params)
					print(changes)
					# update producer.*variables:
					[producer.__setattr__(key, value) for key, value in zip(args, changes)]
					# update producers in production_agents:
					self.production_agents[psector] = producer
			else: # heterogenous functions for different sectors:
				producer = self.production_agents[sector]
				params = [producer.__getattribute__(key) for key in args]
				changes = function(*params)
				[producer.__setattr__(key, value) for key, value in zip(params, changes)]
				self.production_agents[sector] = producer
		# finish updating producers:
		logger.info("[Production Produce] all producers end producing with [{}] production functions ".format(len(kwargs)))
		return self


	def inputDecision(self,iteration):
		"""
		if interval==0:
			if self.raw_output:
				pass
		else:
			she = Shelve("result","./")
			self.raw_output = she.query("gross_output")[interval]
			
		for s in range(self.sector_number):
			self.gross_mat[:,s] = np.random.normal(self.raw_output[s]/float(self.size),float(10**6)/float(self.size),self.size)
			inter_matrix = [mixedPrice(alpha[s],delta[s],prices,m,lamb[s],each) each for each in gross_mat[:,s]]
		
		if intervall == 0:
			# 写入shelve:
			she = Shelve("result","./")
			she.save("gross_mat",:gross_mat)
		else: # 从这里开始是第t+1期:
			she.update("gross_mat",gross_mat)"""

class Producer(object):
	"""
	这是生产商模块: 支持生成某个特定行业的n个企业
	"""
	def __init__(self,**kwargs):
		# 赋值厂商的基本情况:
		self.producer_size = kwargs.get("producer_size", 1000)
		self.producer_sector = kwargs.get("sector", "001")  # 所属行业的编码, 字符串
		self.producers = ["p{}s{}".format(str(index),self.producer_sector) for index in range(self.producer_size)]
		# 复制 producers 的size
		self.producer_input = np.zeros(self.producer_size)
		self.producer_output = np.zeros(self.producer_size)
		# 根据厂商的数量，生成经济条件，此处约定: 所有的经济参数 -- 也就是要计算经济值的变量，应当以 `econ` 命名:
		self.producer_econ_capitals = kwargs.get("producer_econ_capitals", np.random.normal(1000,50,self.producer_size))
		self.producer_econ_costs = kwargs.get("producer_econ_costs", np.random.normal(200,20,self.producer_size))
		self.producer_econ_sales = kwargs.get("producer_econ_sales", np.random.normal(300,30,self.producer_size))
		self.producer_econ_profits = kwargs.get("producer_econ_profits", self.producer_econ_sales - self.producer_econ_costs)
		self.producer_econ_techologies = kwargs.get("producer_econ_techologies", np.random.normal(10,2,self.producer_size))
		# 如果有其他的经济变量，批量在此处添加:
		for key, value in kwargs.items():
			if key not in dir(self) and key.startswith("producer_econ"):
				self.__setattr__(key, value)
		# 生成厂商的元信息:
		metadata = ["producer_input", "producer_output"]
		metadata += [key for key in dir(self) if key.startswith("producer_econ")]
		self.metadata = metadata
		# // end
		logger.info("[Producer Initialise] generate [{}] producers in sector [{}] ".format(self.producer_size, self.producer_sector))


	def _setting_output(self, producer_output_dispatch:object):
		"""
		Set .producer_output, follow the size of .producer_size
		Parameter: 
			- producer_output_dispatch: a function, return `.producer_out` dimension array
		"""
		# call dispatch function:
		_dispatch = producer_output_dispatch()
		if _dispatch.shape == self.producer_output.shape:
			self.producer_output = _dispatch
			return True
		else:
			logger.error("invalid producer_output_dispatch(), expect a `np.ndarray ({})`, but get ({}) ".format(str(self.producer_output),type(_dispatch)))
			return False


	def _setting_input(self, producer_input_dispath:object):
		"""
		Set .producer_input, follow the size of .producer_size
		Parameter:
			- producer_input_dispatch: a function, return `.producer_input` dimension array
		"""
		_dispatch = producer_input_dispath()
		if _dispatch.shape == self.producer_input.shape:
			self.producer_input = _dispatch
			return True
		else:
			logger.error("invalid producer_input_dispath(), expect a `np.ndarray ({})`, but get ({}) ".format(str(self.producer_input),type(_dispatch)))
			return False


	def _setting_econ_variables(self, **kwargs):
		# iterative updating economic variables:
		for key, value in kwargs.items():
			if key in dir(self) and key.startswith("producer_econ"):
				self.__setattr__(key, value)


	def summary(self):
		_metadata = "\n".join(["{}:\t{}".format(key, np.mean(self.__getattribute__(key))) for key in self.metadata])
		_info = """
------------------------------------------------------------
Producer Metadata (Mean)
------------------------------------------------------------
{}
------------------------------------------------------------
""".format(_metadata)
		print(_info)
		return 


	def sync(self,shelve_object:object, iteration):
		"""
		Sync Producer data with Shelve database
		Parameter:
			- shelve_object: inherit from `Shelve`
			- iteration: the node for Shelve database's storage
		"""
		if isinstance(shelve_object, Shelve):
			sync_value = {key:self.__getattribute__(key) for key in self.metadata}
			shelve_object.save(hash_code=iteration, **sync_value)
			logger.info("[Producer Sync] sync [{}] variables into [{}] ".format(len(sync_value), shelve_object.name))
			return True
		else:
			logger.error("[Producer Sync] invalid Shelve Object ")
			return False


class Government(object):
	def __init__(self):
		pass

	def fine(self,obj): # obj: Consumer, Producer
		pass


class Consumer(object):
	"""
	Consumer Agent: including the following functions:
	.saving: ..., interest rate
	.invest: ..., amount
	.consume: ..., product,price,volume
	Parameters:
	:income: income of consumer
	:ir: interest rate
	"""
	def __init__(self,uid,*kargs,**kwargs):
		self.id = uid

	def saving(self,ir,percentage):
		print("[Consumer %s] save %s of income at rate %s"%(self.id,percentage,ir))

	def invest(self):
		pass

	def consume(self):
		pass	


