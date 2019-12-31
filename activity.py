#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Theme: Economic Activities
@Author: Juli
@CreatDate: 2019-12-09
"""

import os
import sys
import numpy as np

try: module_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
except: module_path = "/Users/mario/Document/OneDrive/GitHub/"
sys.path.append(module_path)

import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

########### BaseActivity ###########
class BaseActivity(object):
	def __init__(self):
		self._variables = ""
		self._function = ""
		self.actor = type(self).__name__
		self._actor = type(self).__name__.lower()
		self.scaler = lambda x: x if x>0 else 0	
		logger.info("[{} Initialise] activity starts... ".format(self.actor))

	def recipe(self, *args):
		"""
		菜单: 配置经济活动的主体 (agents):
		Parameters:
			- *args: pipes agents via args
		"""
		if args:
			self.__setattr__("{}_scale".format(self._actor), len(args))
			self.__setattr__("{}_agents".format(self._actor), list(args) if not isinstance(args, list) else args)
			logger.info("[{}] receive [{}] agents in pipe ".format(self.actor, len(self.__getattribute__("{}_agents".format(self._actor)))))
			# mask: masking for agent queue:
			self.agents = self.__getattribute__("{}_agents".format(self._actor))
			return True
		else:
			logger.error("empty recipe queue, specify *args for agents ")
			return False


	def function(self, *args, **kwargs):
		"""
		基类方法: 设置经济变量: _variables 和函数: _function:
		Parameters:
			- *args: variables used in function decisions
			- **kwargs: {"all": function}, specify all the same function to agents, if length of kwargs matches agents, apply them.
		"""
		self._variables = args # if not specify, args depend on types of agents in the queue
		self._function = kwargs


	def execute(self):
		"""
		基类的运行指令: 功能复杂的模块谨慎继承这一方法
		* 但是需要注意的是, 声明指令的指针, 这里的指针只处理`相等大小的agent-function`和`all`指令
		"""
		if not hasattr(self, "agents"):
			logger.error("[{} Execute] failed: empty agents queue, run .recipe() first ".format(self.actor))
			return False
		# verify the size of agents and the size of functions:
		# BaseObject has no agents queue, don't run it standalone.
		if len(self._function) == len(self.agents):
			for index, function in enumerate(self._function.values()):
				params = [self.agents[index].__getattribute__(key) for key in self._variables]
				changes = function(*params)
				[self.agents[index].__setattr__(key, value) for key, value in zip(self._variables, changes)]
		else:
			function = self._function.pop(list(self._function.keys())[0])
			for each in self.agents:
				params = [each.__getattribute__(key) for key in self._variables]
				changes = function(*params)
				[each.__setattr__(key, value) for key, value in zip(self._variables, changes)]


########### BaseConsumer ###########
class BaseConsumer(BaseActivity):
	""" 基类: 消费者的收入和储蓄模块 """
	def __init__(self):
		super(BaseConsumer, self).__init__()

	def recipe(self, *args):
		super(BaseConsumer, self).recipe(*args)

	def function(self, *args, **kwargs):
		super(BaseConsumer, self).function(*args, **kwargs)
		# default function: use `<agent>_econ_capitals`, `<agent>_econ_consumptions`
		if self._variables: pass
		else: self._variables = ["%s_econ_incomes"%self.agents[0]._actor, "%s_econ_consumptions"%self.agents[0]._actor, "%s_econ_savings"%self.agents[0]._actor]

		if self._function: pass
		else: 
			def _default(income, consumption, saving):
				income = np.random.normal(np.mean(income)+30, np.mean(income)//10, len(income))
				consumption = np.random.normal(np.mean(consumption)+20, np.mean(consumption)//10, len(consumption))
				saving = income - consumption
				return income, consumption, saving
			self._function = {"all": _default}

		logger.info("[{} Function] load [{}] functions and [{}] variables ".format(self.actor, len(self._function), len(self._variables)))

	def balance(self):
		if not self._function: self.function()
		# inheritate from BaseActivity:
		super(BaseConsumer, self).execute()
		logger.info("[{} Balance] all agents are balanced with [{}] functions".format(self.actor, len(self._function)))


########### Technology Advance ###########
class Consumption(BaseActivity):
	""" 消费者和政府主体的消费模块 """
	def __init__(self):
		super(Consumption, self).__init__()

	def recipe(self, *args):
		super(Consumption, self).recipe(*args)

	def function(self, *args, **kwargs):
		super(Consumption, self).function(*args, **kwargs)
		# default variables: use `<agent>_econ_capitals`, `<agent>_econ_consumptions`
		if self._variables: pass
		else: self._variables = ["%s_econ_capitals"%self.agents[0]._actor, "%s_econ_consumptions"%self.agents[0]._actor]
		# default functions: use default variables
		if self._function: pass
		else: 
			def _default(capital, consumption):
				# bear in mind, variables are in forms of np.ndarray:
				consumption = np.random.normal(np.mean(capital), np.mean(capital)//30, len(capital))
				capital = capital - consumption
				return capital, consumption
			# if specify `all`, 
			self._function = {"all": _default}

		logger.info("[{} Function] load [{}] functions and [{}] variables ".format(self.actor, len(self._function), len(self._variables)))


	def consume(self):
		if not self._function: self.function()
		super(Consumption, self).execute()
		logger.info("[{} Consume] all agents finish consumption with [{}] functions".format(self.actor, len(self._function)))


class Technology(BaseActivity):
	"""
	技术模块: 允许厂商按照一定的方式进行技术决策
	Functions:
		- recipe: pipes agents into the Environment
		- develop: make technology 
	"""
	def __init__(self):
		super(Technology, self).__init__()

	def recipe(self, *args):
		""" Recipe:  pipes agents into R&D queue """
		super(Technology, self).recipe(*args)

	def function(self, *args, **kwargs):
		""" R&D function for all agents """
		super(Technology, self).function(*args, **kwargs)
		if self._variables: pass
		else: self._variables = ["%s_econ_capitals"%self.agents[0]._actor, "%s_econ_technologies"%self.agents[0]._actor]

		if self._function: pass
		else: 
			def _default(capital, technology):
				technology = np.random.normal(np.mean(capital) * 0.1, (np.mean(capital) * 0.1)/5.0, len(capital))
				capital = capital - technology
				capital = np.array([self.scaler(each) for each in capital])
				return capital, technology
			self._function = {"all": _default}

		logger.info("[{} Function] load [{}] functions and [{}] variables ".format(self.actor, len(self._function), len(self._variables)))


	def develop(self):
		if not self._function: self.function()
		super(Technology, self).execute()
		logger.info("[{} Develop] all agents finish R&D with [{}] functions".format(self.actor, len(self._function)))


class Investment(BaseActivity):
	"""
	投资模块: 允许厂商, 消费者, 政府按照一定的方式进行投资决策
	Functions:
		- recipe: pipes agents into the Environment
		- invest: invest action, use `.capital` and generate `.investment`
		- _set_investment_rate: `float` or function returns `float` value
	"""
	def __init__(self):
		super(Investment, self).__init__()
		self._rate = ""


	def set_investment_rate(self, value_or_function=None):
		if hasattr(value_or_function, "__call__"):
			self._rate = value_or_function()
		else:
			if not value_or_function: self._rate = np.random.random()
			else: self._rate = value_or_function


	def recipe(self, *args):
		""" 菜单: 配置进行投资的主体 (agents) """
		super(Investment, self).recipe(*args)
 

	def function(self, *args, **kwargs):
		"""
		设定投资函数: !remember the last argument should be `investment_rate`
		"""
		super(Investment, self).function(*args, **kwargs)

		if self._variables: 
			pass
		else:
			_sample = self.agents[0]
			_vars = [each for each in dir(_sample) if each.endswith("capitals") or each.endswith("econ_investments")]
			# // 如果输入的主体队列是不同的主体，可以这么做、但不建议，代码不会区分，但没必要把不同主体放一起吧?
			if _vars:
				inv_variable = "{}_econ_investments".format(type(_sample).__name__.lower())
				if inv_variable not in _vars:
					[each.__setattr__(inv_variable, np.zeros(each.__getattribute__(_vars[0]).shape)) for each in self.agents]
					_vars.append(inv_variable)
				# if not, don't append new vars
				self._variables = _vars
			else:
				logger.error("invest variable missing, specify `variable` for agents ")
				return False

		if self._function:
			pass
		else:
			def _default(capital, investment, investment_rate): # investment is benefit part:
				investment = np.random.normal(np.mean(capital) * investment_rate, (np.mean(capital) * investment_rate) // 10, len(capital))
				capital = capital - investment
				return capital, investment

			self._function = {"all": _default}
		logger.info("[{} Function] load [{}] functions and [{}] variables ".format(self.actor, len(self._function), len(self._variables)))


	def invest(self):
		if not self._function: self.function()
		if not self._rate: self.set_investment_rate()

		if len(self._function) == len(self.agents):
			for index, function in enumerate(self._function.values()):
				params = [self.agents[index].__getattribute__(key) for key in self._variables]
				params.append(self._rate) # fundamental: put investment_rate at the bottom
				changes = function(*params)
				[self.agents[index].__setattr__(key, value) for key, value in zip(self._variables, changes)]
		else:
			function = self._function.pop(list(self._function.keys())[0])
			for each in self.agents:
				params = [each.__getattribute__(key) for key in self._variables]
				params.append(self._rate) # fundamental: put investment_rate at the bottom
				changes = function(*params)
				[each.__setattr__(key, value) for key, value in zip(self._variables, changes)]
		logger.info("[{} Invest] all agents end investing with [{}] invest actions ".format(self.actor, len(self._function)))


########### Production ###########
class Production(BaseActivity):
	"""
	生产模块: 将定制后的`厂商`传入本模块，经过生产条件(模块)的加工后，更新厂商的经济属性
	Functions:
		- recipe: 配置不同行业的厂商进入生产序列
		- produce: 生产函数，根据条件更新厂商指定的经济属性
	"""
	def __init__(self):
		super(Production, self).__init__()

	def recipe(self,*args):
		""" recipe: pipes producers into production recipe """
		super(Production, self).recipe(*args)
			

	def function(self, *args, **kwargs):
		""" set produce function """
		super(Production, self).function(*args, **kwargs)
		if self._function: pass
		else:
			def _default(output, costs):
				output = np.random.normal(np.mean(output) * 1.1, np.mean(output)//10, len(output))
				costs = np.random.normal(np.mean(costs) * 1.1, np.mean(costs)//10, len(costs))
				return [output, costs]
			kwargs = {"all":_default}
		self._function = kwargs

		if self._variables: pass
		else: self._variables = ["producer_econ_output","producer_econ_costs"]
		logger.info("[{} Function] load [{}] functions and [{}] variables ".format(type(self).__name__, len(self._function), len(self._variables)))


	def produce(self):
		"""
		生产决策: 根据给定的生产决策函数 `_function` 更新厂商的经济变量 `_variables`		
		"""
		if not self._function: self.function()
		# update production variables:
		for sector, function in self._function.items():
			if sector == "all":
				for index, producer in enumerate(self.agents):
					params = [producer.__getattribute__(key) for key in self._variables]
					# call production function:
					changes = function(*params)
					# update producer.*variables:
					[producer.__setattr__(key, value) for key, value in zip(self._variables, changes)]
					# update producers in production_agents: (in memory)
					# self.production_agents[psector] = producer
			else: # heterogenous functions for different sectors:
				if len(self.agents) == len(self._function):
					index = 0
					for key, function in self._function:
						params = [self.agents[index].__getattribute__(key) for key in self._variables]
						changes = function(*params)
						[self.agents[index].__setattr__(key, value) for key, value in zip(params, changes)]
						index += 1
				else:
					logger.error("[{} Produce] [{}] agents can't be assigned to [{}] functions ".format(type(self).__name__, len(self.agents), len(self._function)))
		# finish updating producers:
		logger.info("[{} Produce] all producers end producing with [{}] production functions ".format(type(self).__name__, len(self._function)))

