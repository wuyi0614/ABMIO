"""
@Theme: CES module
@Author: Juli
@CreatDate: 2019-12-26
"""
import pandas as pd

PATH = '/Users/juli/Desktop/Graduation_Project/carbon_trade/codes/ces_data/'
Number_sec = 139

class CES(object):
	def __init__(self,shelve_path,shelve_name):
		self.she = Shelve(shelve_name,shelve_path)
	
	def _load_producer_settings(self):
		alpha = self.she.query("firm_alpha_8xs")
		delta = self.she.query('firm_delta_8xs')
		#prices = pd.read_csv(self.path + 'commodity_prices' + interval + '(1xs).csv')
		prices = self.she.query('commodity_price')
		m = self.she.query('firm_inter_coef_1xs')
		lamb = self.she.query('firm_lambda_1xs')

	@staticmethod
	def _mixed_price(alpha,price1,price2,delta):
		return (alpha * price1**(1-delta) + (1-alpha)* price2**(1-delta))**(1/(1-delta))

	@staticmethod
	def mixedPrice(alpha,delta,price,m,lamb,X):
	#--------- price calculation------------------
		alpha,delta,m,lamb += [99]
		pr_K = price[10] 
		pr_L = price[11]
		pr_momg = _mixed_price(alpha[1],price[2],price[3],delta[1])
		pr_mcmo = _mixed_price(alpha[2],price[1],pr_momg,delta[2])
		pr_oilcok = _mixed_price(alpha[3],price[4],price[5],delta[3])
		pr_Fn = _mixed_price(alpha[4],pr_mcmo,pr_oilcok,delta[4])
		pr_E = _mixed_price(alpha[5],price[6],pr_Fn,delta[5])
		pr_KL = _mixed_price(alpha[6],pr_K,pr_L,delta[6])
		pr_KEL = _mixed_price(alpha[7],pr_KL,pr_E/lamb,delta[7])
		pr_INT = m[1] * price[7] + m[2] * price[8] + m[3] * price[9]
		pr_x = _mixed_price(alpha[8],pr_KEL,pr_INT,delta[8])

	#----------- input calculation--------------------
		KEL = alpha[8] * (pr_x/pr_KEL)**(delta[8]) * X
		INT = (1-alpha[8]) * (pr_x/pr_INT)**(delta[8]) * X
		KL = alpha[7] * (pr_KEL/pr_KL)**(delta[7]) * KEL
		E = lamb^(delta[7]-1) * (1-alpha[7]) * (pr_KEL/pr_E)**(delta[7]) * KEL
		K = alpha[6] * (pr_KL/pr_K)**(delta[6]) * KL
		L = (1-alpha[6]) * (pr_KL/pr_L)**(delta[6]) * KL
		ELE = alpha[5] * (pr_E/price[6])**(delta[5]) * E
		Fn = (1-alpha[5]) * (pr_E/pr_Fn)**(delta[5]) * E
		Z2 = alpha[4] * (pr_Fn/pr_mcmo)**(delta[4]) * Fn
		Z3 = (1-alpha[4]) * (pr_Fn/pr_mcmo)**(delta[4]) * Fn
		Fn4 = alpha[3] * (pr_oilcok/price[4])**(delta[3]) * Z3
		Fn5 = (1-alpha[3]) * (pr_oilcok/price[5])**(delta[3]) * Z3
		Fn1 = alpha[2] * (pr_mcmo/price[1])**(delta[2]) * Z2
		Z1 = (1-alpha[2]) * (pr_mcmo/price[1])**(delta[2]) * Z2
		Fn2 = alpha[1] * (pr_momg/price[2])**(delta[1]) * Z1
		Fn3 = (1-alpha[1]) * (pr_momg/price[3])**(delta[1]) * Z1
		int1 = INT * m[1]
		int2 = INT * m[2]
		int3 = INT * m[3]	

		res = {'Fn1':Fn1,'Fn2':Fn2,'Fn3':Fn3,'Fn4':Fn4,'Fn5':Fn5,'ELE':ELE,
				'int1':int1,'int2':int2,'int3':int3,'L':L,'K':K}
		return res
