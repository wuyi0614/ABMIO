"""
@Theme: Market module
@Author: Juli
@CreatDate: 2019-12-09
"""
import os
import sys
import numpy as np

try: module_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
except: module_path = "/Users/mario/Document/OneDrive/GitHub/"
sys.path.append(module_path)

from ABMIO.activity import BaseActivity

import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BaseMarket(BaseActivity):
	def __init__(self):
		""" BaseClass: define Market objects """
		# 市场的特性是，主体不直接参与，只输入经济变量
		super(BaseMarket, self).__init__()

	def recipe(self, *args):
		"""
		BaseMethod: inherit from BaseActivity, pipe agents in the queue
		Parameters:
			- *args: receive agents that are to be updated
		"""
		super(BaseMarket, self).recipe(*args)

	def setting_variables(self, **kwargs):
		"""
		BaseMethod: set economic variables for agents:
		Parameters:
			- **kwargs: accept <agent_market_econ_variable>=value
		"""
		if kwargs:
			for key ,value in kwargs.items():
				[agent.__setattr__(key, value) for agent in self.agents]
			self._variables = list(kwargs.keys())
			# update pre-defined variables
		else:
			# add <agent>_<market>_econ_demands and <agent>_<market>_econ_supplies on Agent (not agents):
			# add <agent>_<market>_econ_prices on agents:
			for agent in self.agents:
				_market_agent = "{}_{}".format(agent._actor, self._actor)
				_market_variables = ["econ_demands", "econ_supplies", "econ_prices"]
				_market_variables = ["{}_{}".format(_market_agent, each) for each in _market_variables]
				self._variables = _market_variables
				for var in _market_variables:
					if var.endswith("demands") and not hasattr(agent, var):
						# search similar variables: `input`, `consumptions`
						_similar_vars = [each for each in dir(agent) if each.endswith("econ_consumptions")]
						if _similar_vars:
							_demands = np.sum(agent.__getattribute__(_similar_vars.pop()))
						else:
							_demands = np.zeros(agent.get_size())
						agent.__setattr__(var, _demands)
					elif var.endswith("supplies") and not hasattr(agent, var):
						# search similar variables: `output`, even for carbon market, use `carbon_agent_econ_output`
						_similar_vars = [each for each in dir(agent) if each.endswith("econ_output")]
						if _similar_vars:
							_supplies = np.sum(agent.__getattribute__(_similar_vars.pop()))
						else:
							_supplies = np.zeros(agent.get_size())
						agent.__setattr__(var, _supplies)
					else:
						if not hasattr(agent, var):
							_prices = np.random.normal(1, 0.01, agent.get_size())
							agent.__setattr__(var, _prices)

			logger.info("[{} Setting] variables of agent [{}] are prepared ".format(self.actor, agent.actor))


	def function(self, *args, **kwargs):
		"""
		BaseMethod: market function and variables settings
		Parameters:
			- *args: economic variables in market operation
			- **kwargs: function=`market function`
		"""
		super(BaseMarket, self).function(*args, **kwargs)
		if self._variables: pass
		else: self.setting_variables() # default functions: use default variables

		if self._function: pass
		else: 
			def _default(demand, supply, price):
				# bear in mind, variables are in forms of np.ndarray:
				price = price * self.weighted_random(lower=0.9, upper=1.1, weight=demand-supply)
				return demand, supply, price
			# if specify `all`, 
			self._function = {"all": _default}
			# 如果对属于不同产业部门的producer使用不同的价格作用函数，在._function中指定每个部门的function即可
		logger.info("[{} Function] load [{}] functions and [{}] variables ".format(self.actor, len(self._function), len(self._variables)))

	def is_balance(self, *args):
		"""
		BaseMethod: market pursues balance between variables
		Parameters:
			- *args: variables (size depends on agents)
		Return:
			- boolean: True for balanced, False for unbalanced
		"""
		# if size of args > 2:
		_sum = [np.sum(each) for each in args]
		_verify_median, _verify_mean = [], []
		for each in _sum:
			_verify_median.append(True if (each - np.median(_sum)) == 0 else False)
			_verify_mean.append(True if (each - np.mean(_sum)) == 0 else False)

		if any(_verify_mean) and any(_verify_median): return True
		else: return False
		
	def equilibrium(self):
		""" BaseMethod: equilibrium calculation, functions and variables from .function """
		if not self._function: self.function()
		if not self._variables: self.setting_variables()
		# Market equilibrium: call <variable>_econ_demands, <variable>_econ_supplies to determine econ_prices:
		super(BaseMarket, self).execute()
		logger.info("[{} Equilibrium] market price is adjusted by [{}] functions".format(self.actor, len(self._function)))


class Commodity(BaseMarket):
	def __init__(self):
		super(Commodity, self).__init__()

	def recipe(self, *args):
		super(Commodity, self).recipe(*args)

	def setting_variables(self, **kwargs):
		super(Commodity, self).setting_variables(**kwargs)

	def function(self, *args, **kwargs):
		""" Commodity Market: specify unique function to it """
		super(Commodity, self).function(*args, **kwargs)

	def equilibrium(self):
		super(Commodity, self).equilibrium()


class Carbon(BaseMarket):
	def __init__(self):
		super(Carbon, self).__init__()

	def recipe(self, *args):
		super(Carbon, self).recipe(*args)

	def setting_variables(self, **kwargs):
		super(Commodity, self).setting_variables(**kwargs)

	def function(self, *args, **kwargs):
		""" Carbon Market: specify unique function to it """
		super(Carbon, self).function(*args, **kwargs)

	def equilibrium(self):
		super(Carbon, self).equilibrium()


class Electricity(BaseMarket):
	def __init__(self):
		super(Electricity, self).__init__()

	def recipe(self, *args):
		super(Electricity, self).recipe(*args)

	def setting_variables(self, **kwargs):
		super(Electricity, self).setting_variables(**kwargs)

	def function(self, *args, **kwargs):
		""" Electricity Market: specify unique function to it """
		super(Electricity, self).function(*args, **kwargs)

	def equilibrium(self):
		super(Electricity, self).equilibrium()

	