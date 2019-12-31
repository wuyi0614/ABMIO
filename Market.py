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
		self.__setattr__("{}_econ_prices".format(self._actor), np.random.random)

	def function(self, *args, **kwargs):
		"""
		BaseMethod: market function and variables settings
		Parameters:
			- *args: economic variables in market operation
			- **kwargs: function=`market function`
		"""
		super(BaseMarket, self).function()



class CommodityMarket(Producer,Consumer):
	def __init__(self):
		pass

	def balance(self):
		"""
		Balance between demand and supply
		"""
		if demand == supply:
			self.productPrice = 10
		else:
			self.productPrice = self.productPrice * (S/D)



class CarbonMarket(Producer,Government):
	def __init__(self):
		pass


class ElectricityMarket(Producer):
	def __init__(self):
		pass