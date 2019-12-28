"""
@Theme: Parameter module
@Author: Juli
@CreatDate: 2019-12-27
"""

"""
import shelve
import pandas as pd
PATH = '/Users/juli/Desktop/Graduation_Project/carbon_trade/codes/ces_data/'
db = shelve.open("/Users/juli/Desktop/Graduation_Project/carbon_trade/ABM/Parameter")
#list(db.keys())
db["firm_alpha_8xs"] = pd.read_csv(PATH + 'firms_alpha(8xs).csv')
db["firm_delta_8xs"] = pd.read_csv(PATH + 'firms_delta(8xs).csv')
db['firm_lambda_1xs'] = pd.read_csv(PATH + 'firms_lambda(1xs).csv')
db['firm_capital_coef_1xs'] = pd.read_csv(PATH + 'firms_capital_coef(1xs).csv')
db['firm_export_coef_1xs'] = pd.read_csv(PATH + 'firms_export_coef(1xs).csv')
db['firm_import_coef_1xs'] = pd.read_csv(PATH + 'firms_import_coef(1xs).csv')
db['firm_inter_coef_1xs'] =pd.read_csv(PATH + 'firms_m(1xs).csv')
db['firm_tax_rate_1xs'] = pd.read_csv(PATH + 'firms_tax_rate(1xs).csv')
db['firm_tech_adju_1'] = pd.read_csv(PATH + 'firms_tech_xi(1).csv')
db['commodity_price'] = pd.read_csv(PATH + 'commodity_prices0(1xs).csv')
db['energy_calorie_1x5'] = pd.read_csv(PATH + 'governments_an.csv')
db['emission_factor_1x5'] = pd.read_csv(PATH + 'governments_bn.csv')
db['energy_oxidation_1x5'] = pd.read_csv(PATH + 'governments_cn.csv')
db['government_consumption_coef_1xs'] = pd.read_csv(PATH + 'governments_consumption_coef(1xs).csv')
db['government_yita_ixs'] = pd.read_csv(PATH + 'governments_yita(ixs).csv')
db['government_subsidy_rate_1'] = pd.read_csv(PATH + 'governments_subsidy_rate(1).csv')
db['penalty_rate_1'] = pd.read_csv(PATH + 'governments_penalty_rate(1).csv')
db['national_tech_1'] = pd.read_csv(PATH + 'national_tech_level(1).csv')
db['consumer_wage_coef_1xs'] = pd.read_csv(PATH + 'consumers_wage_coef.csv')
db['consumer_consum_coef_hxs'] = pd.read_csv(PATH + 'consumption_share(hxs).csv')
db['carbon_price_ref_1'] = pd.read_csv(PATH + 'governments_carbon_price_reference(1).csv')
#db['io_table'] = pd.read_csv(PATH + 'raw_IOtable.csv')
db.close()
"""



#----------------------

import shelve
import os
import re
import pandas as pd
from itertools import chain

import logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Shelve(object):
    module_path = os.path.dirname(os.path.abspath(__file__))
    def __init__(self,name,path=None):
        if not path: path = self.module_path
        self.path = path
        self.name = name
        self.db = ""

    
    def to_md5(self,string):
        return hashlib.md5(string.encode("utf8")).hexdigest()        
    

    def open(self):
        self.db = shelve.open("{}/{}".format(self.path,self.name))
        return self


    def close(self):
        if self.db: self.db.close()
        else: self.db = ""

    
    def save(self,hash_code,**kwargs):
        db = shelve.open("{}/{}".format(self.path,self.name))
        try:
            if kwargs:
                db[hash_code] = {k:v for k,v in kwargs.items()}
                logger.info("[Shelve save] save [{}] at [{}] ".format(hash_code,self.name))
        except Exception as e:
            logger.error("[Shelve save] failed: [%s] "%e)
        finally:
            db.close()
        
    
    def load(self,path=None):
        # name can be ambiguous(only name) or a path
        if path:
            if os.path.isfile(path): name = path
        else:
            name = "{}/{}".format(self.path,self.name)
        try:
            db = shelve.open(name)
            mapping = {k:v for k,v in db.items()}
            db.close()
            return mapping
        
        except Exception as e: 
            logger.error("[Shelve load] failed %s "%e)
            return False
            
    
    def delete(self,hash_code:str="",q:str="") -> bool:
        if hash_code:
            db = shelve.open("{}/{}".format(self.path,self.name))
            if hash_code in db: 
                db.pop(hash_code)
                return True
            else: 
                return False
            db.close()
        elif q: # econ_variable
            db = shelve.open("{}/{}".format(self.path,self.name))
            for key, value in db.items(): # dicts
                if q in value:
                    db[key].pop(q)
                    db.close()
                    return True
                else:
                    next
            db.close()
        else:
            return False

    
    
    def query(self,hash_code:str="",q:str="") -> dict:
        """ Query objects
        :hash_code: query hash value
        :q: query phrase, give token or string to search
        """
        mapping = self.load()
        if mapping:
            if hash_code:
                return mapping[hash_code]
            elif q:
                submapping = mapping.values()
                for each in submapping: # dicts
                    if q in each:
                        return each
                    else:
                        next
                return False
        else:
            return False
    
    
    def update(self,hash_code,obj):
        """ Object update
        :hash_code: query hash value
        :**kwargs: example: <value_type> = object
        """
        old = self.load()
        if hash_code in old:
            match = old[hash_code]
            if not isinstance(match,list):
            	match = [match]

            if not isinstance(obj,list):
            	obj = [obj]
            
            match += obj
            # end
            self.save(hash_code,match)
            logger.info("[Shelve update] update 1 record: %s"%hash_code)
            return True
        else: # if hash_code not in mapping
            return False