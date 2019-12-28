"""
@Theme: Agents module
@Author: Juli
@CreatDate: 2019-12-09
"""

import os

__ALL__ = ["Producer","Government","Consumer"]

class Producer(object):
	def __init__(self):
		pass

	def input_decision(self,IO:object):
		pass


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


	