"""
@Theme: __init__ module
@Author: Juli
@CreatDate: 2019-12-09
"""

import os
from .Agent import *
from .Market import *


# vectorise : firms = [100,110,180,99,50]
# object: firms = [Agent.firm.id==1,Agent.firm.id==2]

def run(firm_num=1000):
	io = IO(io_path)
	# 生成主体:
	agents = []
	for i in range(firm_num):
		# 正态化产值:
		output = normal(io.gross_output)[i]

		agents += [Producer(id=i,output=output)]


