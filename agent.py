"""
@Theme: Agents module
@Author: Juli
@CreatDate: 2019-12-09
"""

import os
import re
import sys
import math
import numpy as np
import seaborn as sns

try: module_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
except: module_path = "/Users/mario/Document/OneDrive/GitHub/"
sys.path.append(module_path)

# from ABMIO.ces_model import CES

import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# import Agent.Producer
PATH = '/Users/juli/Desktop/Graduation_Project/carbon_trade/codes/ces_data/'

class AgentError(Exception):
	pass

__ALL__ = ["Producer","Government","Consumer"]

class BaseAgent(object):
	def __init__(self):
		""" BaseClass for all-type Agents """
		self.actor = type(self).__name__
		self._actor = type(self).__name__.lower()
		# natural selector: interesting gadget
		self.scaler = lambda x: x if x>0 else 0
        # use (negativ, postivve operator) to aviod `math.OverflowError`
		self.logistic = lambda x: 1/(1+math.exp(-x)) if x>0 else 1 - 1/(1+math.exp(x))

	def lineplot(self, *args, **kwargs):
		"""
		基类方法: 绘制折线图 (based on size of agents)
		Parameters:
			- *args: variables are to be displayed
            - **kwargs: axis_x: default as agents
		"""
		X = kwargs.get("axis_x", list(range(self.get_size())))
		Y = self.__getattribute__(self.get_econ_variables()[0]) if self.get_econ_variables() else np.random.random(self.get_size())
		sns.lineplot(X, Y)
		pass # //TODO

	def boxplot(self, *args):
		"""
		基类方法: 绘制折线图 (based on size of agents)
		Parameters:
			- *args: variables are to be displayed
		"""
		pass # //TODO


	def excel(self):
		"""
		基类方法: 输出为excel文件 (.xls)
		Parameters:
			- *args: variables output
		"""
		pass # //TODO


	def jsonify(self):
		"""
		基类方法: 输出为json文件 (.txt)
		Parameters:
			- *args: variables output
		"""
		pass # //TODO		

	def ab_scaler(self, lower, upper, vector):
		if not isinstance(vector, list): vector = [vector]
		k = (upper - lower) / (max(vector) - min(vector))
		vector = [(lower + k * (x - min(vector))) for x in vector]
		return np.array(vector)

	def weighted_random(self, lower, upper, weight):
		"""
		基类方法: 给定权重和数值上下限，返回校准后的随机数
		* if weight>0, positive increment; else negative decline
		"""
		_weight = self.logistic(weight) / 100.0 # value in [-1,1] ~ logis(0)=0.5
		return np.random.uniform(lower+_weight, upper+_weight, 1)[0]

	def get_size(self):
		return self.__getattribute__("{}_size".format(self._actor))

	def get_econ_variables(self):
		return [each for each in dir(self) if each.startswith("{}_econ".format(self._actor))]
        
	def calibrate(self, syntax):
		"""
		基类方法: 经济变量校准，传入表达式句法, 示例: 
		syntax = "consumer_econ_saving_rates=consumer_econ_savings/consumer_econ_incomes"
		ie. `储蓄率表达式计算`
		"""
		# search variables:
		args_expr = re.compile("(\w+_*\w+)")
		args = args_expr.findall(syntax)
		# update variables:
		expr_args = ["{}.{}".format(self._actor, arg) for arg in args]
		_syntax = args_expr.sub("{}", syntax)
		syntax = _syntax.format(*expr_args)
		# eval syntax into an expression:
		expression = syntax.split("=")[-1]

		if hasattr(self, args[0]):
			self.__setattr__(args[0], eval(expression))
			logger.info("[{} Calibrate] carlibrate [{}]".format(self.actor, args[0]))
		else:
			logger.error("[{} Calibrate] failure calibration [{}] missing".format(self.actor, args[0]))
			return False


	def summary(self):
		""" 基类方法: 经济变量概述, 返回经济变量的均值统计 """
		_metadata = ["{:<40}|{:>19.2f}".format(key, np.mean(self.__getattribute__(key))) for key in dir(self) if "econ" in key.split("_")]
		_info = """
------------------------------------------------------------
{} Metadata (method: Mean, unit: 10^4 Yuan)
------------------------------------------------------------
{}
------------------------------------------------------------
""".format(self.actor, "\n".join(_metadata))
		print(_info)
		return 

	def setting_variables(self, **kwargs):
		"""
		基类方法: 调整经济变量
		Parameters:
			- **kwargs: input all variables named as `<agent>_econ_<var>`
		"""
		# iterative updating economic variables:
		for key, value in kwargs.items():
			if key.startswith("{}_econ".format(self._actor)):
				pass
			elif "econ" in key.split("_"):
				key = "{}_{}".format(self._actor, key)

			self.__setattr__(key, value)
			logger.info("[{}] set variable: [{}]".format(self.actor, key))


	def preload(self, shelve_object:object, iteration, label=""):
		"""
		基类方法: 从现有的数据库中加载经济数据
		Parameters:
			- shelve_object: Shelve object with nodes' data
			- iteration: the node for Shelve database's storage
			- label: label for Agent's classification
		"""
		node = "node{}".format(iteration)
		if label: load_label = "{}_{}".format(self.actor, label)
		else: load_label = self.actor

		if type(shelve_object).__name__ == "Shelve":
			result = shelve_object.query(node)
			if result:
				_load, preload_data = [], result[load_label]
				for key, value in preload_data.items():
						self.__setattr__(key, value)
						_load += [key]
				logger.info("[{} Preload] load [{}] variables from database [{}] ".format(self.actor, len(_load), shelve_object.name))
			else:
				logger.warning("[{} Preload] can't find node [{}] in database [{}] ".format(self.actor, node, shelve_object.name))
		else:
			logger.error("[{} Preload] invalid Shelve Object ".format(self.actor))
			return False


	def sync(self, shelve_object:object, iteration, label=""):        
		"""
		BaseMethod: Sync agent data with Shelve database
		Parameter:
			- shelve_object: inherit from `Shelve`
			- iteration: the node for Shelve database's storage
			- label: label for Agent's classification
		"""
		if label: sync_label = "{}_{}".format(self.actor, label)
		else: sync_label = self.actor

		if type(shelve_object).__name__ == "Shelve":
			object_value = {key:self.__getattribute__(key) for key in dir(self) if key.startswith("{}_econ".format(self._actor))}
			sync_node = "node{}".format(iteration)

			# define <object name> and sync {<object name>/label: object_value}
			sync_value = {sync_label : object_value}
			shelve_object.update(hash_code=sync_node, **sync_value)
			logger.info("[{} Sync] sync [{}] variables into [{}] at node [{}] ".format(sync_label,len(sync_value), shelve_object.name, sync_node))
			return True
		else:
			logger.error("[{} Sync] invalid Shelve Object ".format(sync_label))
			return False


class Producer(BaseAgent):
	"""
	这是生产商模块: 支持生成某个特定行业的n个企业
    需要说明的是，默认的厂商投入 (econ_input) 是和消费量保持一致的变量
	"""
	def __init__(self,**kwargs):
		super(Producer, self).__init__()
		# 赋值厂商的基本情况:
		self.producer_size = kwargs.get("size", 1000)
		self.producer_sector = kwargs.get("sector", "all")  # 所属行业的编码, 字符串
		self.producers = ["p{}s{}".format(str(index),self.producer_sector) for index in range(self.producer_size)]
		# 根据厂商的数量，生成经济条件，此处约定: 所有的经济参数 -- 也就是要计算经济值的变量，应当以 `econ` 命名:
		self.producer_econ_capitals = kwargs.get("producer_econ_capitals", np.random.normal(1000,50,self.producer_size))
		self.producer_econ_costs = kwargs.get("producer_econ_costs", np.random.normal(200,20,self.producer_size))
		self.producer_econ_sales = kwargs.get("producer_econ_sales", np.random.normal(300,30,self.producer_size))
		self.producer_econ_profits = kwargs.get("producer_econ_profits", self.producer_econ_sales - self.producer_econ_costs)
		self.producer_econ_technologies = kwargs.get("producer_econ_technologies", np.random.normal(10,2,self.producer_size))
		self.producer_econ_tax_rates = kwargs.get("producer_econ_tax_rates", np.random.random(self.producer_size))
		self.producer_econ_taxes = kwargs.get("producer_econ_taxes", self.producer_econ_tax_rates * self.producer_econ_sales)
		self.producer_econ_consumptions = kwargs.get("producer_econ_consumptions", np.random.normal(100,10,self.producer_size))
		# 复制 producers 的size
		self.producer_econ_input = self.producer_econ_consumptions
		self.producer_econ_output = self.producer_econ_sales
		# 如果有其他的经济变量，批量在此处添加:
		for key, value in kwargs.items():
			if key not in dir(self) and key.startswith("producer_econ"):
				self.__setattr__(key, value)
		# // end
		logger.info("[{} Initialise] generate [{}] agents in sector [{}] ".format(self.actor, self.producer_size, self.producer_sector))

	def setting_variables(self, **kwargs):
		super(Producer, self).setting_variables(**kwargs)

	def summary(self):
		super(Producer, self).summary()

	def preload(self, shelve_object:object, iteration, label):
		super(Producer, self).preload(shelve_object, iteration, label)

	def sync(self,shelve_object:object, iteration, label):
		super(Producer, self).sync(shelve_object, iteration, label)


class Government(BaseAgent):
	def __init__(self, **kwargs):
		super(Government, self).__init__()
		# basis of agent
		self.government_size = 1
		self.government = kwargs.get("government", "all")
		# assign the basic account of government:
		self.government_econ_taxes = kwargs.get("government_econ_tax", np.random.normal(100, 10, self.government_size))
		self.government_econ_tax_rates = kwargs.get("government_econ_tax_rate", np.random.random())
		self.government_econ_capitals = kwargs.get("government_econ_capital", np.random.normal(500, 10, self.government_size))
		self.government_econ_subsidies = kwargs.get("government_econ_subsidy", np.random.normal(-200, 20, self.government_size)) # subsidy is normally negative value
		self.government_econ_penalties = kwargs.get("government_econ_subsidy", np.random.normal(200, 20, self.government_size))
		self.government_econ_penalty_rates = kwargs.get("government_econ_tax_rate", np.random.random())
		self.government_econ_consumptions = self.government_econ_capitals // 10
        # if any other kwarg:
		for key, value in kwargs.items():
			if key.startswith("government_econ"):
				pass
			elif "econ" in key.split("_"):
				key = "{}_{}".format(self._actor, key)
			self.__setattr__(key, value)
		# //end
		logger.info("[{} Initialise] generate [{}] agents".format(self.actor, self.government))

	def setting_variables(self, **kwargs):
		super(Government, self).setting_variables(**kwargs)

	def summary(self):
		super(Government, self).summary()

	def preload(self, shelve_object:object, iteration, label):
		super(Producer, self).preload(shelve_object, iteration, label)

	def sync(self,shelve_object:object, iteration, label):
		super(Producer, self).sync(shelve_object, iteration, label)


class Consumer(BaseAgent):
	"""	Consumer Agent """
	def __init__(self, *kargs, **kwargs):
		super(Consumer, self).__init__()
		# basis of agents:
		self.consumer_size = kwargs.get("size", 1000)
		# following are the economic variables:
		self.consumer_econ_incomes = kwargs.get("consumer_econ_incomes", np.random.normal(200, 20, self.consumer_size))
		self.consumer_econ_consumptions = kwargs.get("consumer_econ_consumptions", np.random.normal(100, 30, self.consumer_size))
		self.consumer_econ_tax_rates = kwargs.get("consumer_econ_tax_rates", np.random.random(self.consumer_size))
		self.consumer_econ_taxes = kwargs.get("consumer_econ_taxes", self.consumer_econ_incomes * self.consumer_econ_tax_rates)
		# verify if saving rate is negative or positive:	
		self.consumer_econ_savings = kwargs.get("consumer_econ_savings", self.consumer_econ_incomes - self.consumer_econ_consumptions - self.consumer_econ_taxes)
		self.consumer_econ_savings = np.array([self.scaler(each) for each in self.consumer_econ_savings])
		self.consumer_econ_saving_rates = kwargs.get("consumer_econ_saving_rates", self.consumer_econ_savings / self.consumer_econ_incomes)

		# update variables if variables are assigned:
		for key, value in kwargs.items():
			if key not in dir(self) and key.startswith("consumer_econ"):
				self.__setattr__(key, value)
		# // end
		logger.info("[{} Initialise] generate [{}] agents ".format(self.actor, self.consumer_size))		


	def setting_variables(self, **kwargs):
		super(Consumer, self).setting_variables(**kwargs)

	def summary(self):
		super(Consumer, self).summary()

	def preload(self, shelve_object:object, iteration, label):
		super(Producer, self).preload(shelve_object, iteration, label)

	def sync(self,shelve_object:object, iteration, label):
		super(Producer, self).sync(shelve_object, iteration, label)
