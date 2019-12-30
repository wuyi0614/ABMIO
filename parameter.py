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
import hashlib

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
        self.db = shelve.open("{}/{}".format(self.path,self.name), writeback=True)
        return self


    def close(self):
        if self.db: self.db.close()
        else: self.db = ""

    
    def save(self,hash_code,**kwargs):
        """ 在模型的场景中，shelve的结构是:
        1. {"node1":{"<Agent>":{"agent_econ_var1":...,"agent_econ_var2":...}}}
        2. {"node1":{"<Agent_label>":{"agent_econ_var1":...,"agent_econ_var2":...}}}
        其中`node1` 是iteration, `label` 是根据同一类主体不同标签的分类符
        """
        she = self.open()
        try:
            if kwargs:
                she.db[hash_code] = {k:v for k,v in kwargs.items()}
                logger.info("[Shelve save] save [{}] at [{}] ".format(hash_code,self.name))
        except Exception as e:
            logger.error("[Shelve save] failed: [%s] "%e)
        finally:
            she.close()
        
    
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
            
    
    def delete(self,hash_code:str="",label:str=""):
        if hash_code:
            if self.query(hash_code):
                she = self.open()
                she.db.pop(hash_code)
                she.close()
                return True
            else: 
                return False
        elif label: # econ_variable
            mapping = self.load()
            she = self.open()
            if label in mapping.keys():
                she.db.pop(label)
                she.close()
                return True
            
            for node, value in mapping.items(): # dicts
                if label in value:
                    she.db[node].pop(label)
                    she.close()
                    return True
                else:
                    for key, objects in value.items():
                        if label in objects:
                            she.db[node][key].pop(label)
                            she.close()
                            return True
            she.close()
            return False
        else:
            return False

    
    def query(self,hash_code:str):
        """ Query objects
        :hash_code: exact hash_code match
        :q: query phrase, match variables under hash_code
        """
        she = self.open()
        if hash_code in she.db:
            result = she.db[hash_code]
        else:
            result = {}
        she.close()
        return result

    
    def update(self,hash_code,**kwargs):
        """ Object update
        :hash_code: query e.g. `node1` 
        :**kwargs: **{"<symbol>": {"var1":obj, "var2":obj}}
        """
        result = self.query(hash_code)
        if result:
            _update = []
            for key, value in kwargs.items(): # here, key is the label
                if key in result:
                    # only suport overwriting not appending
                    result[key] = value
                    _update += [key]
                else:
                    next
            self.save(hash_code, **result)
            logger.info("[Shelve update] update [{}] at [{}] ".format(", ".join(_update), self.name))
        else:
            self.save(hash_code, **kwargs)
            logger.info("[Shelve save] create [{}] at [{}] ".format(hash_code, self.name))
        return True
        