
import sqlite3
from pathlib import Path
import os
import json      

import pandas as pd

import logging

from option_trader.settings import app_settings   
from option_trader.settings import schema as schema  
from option_trader.admin import user
from option_trader.utils.monitor import refresh_monitor_list
from option_trader.consts import asset

from datetime import datetime
from time import ctime
from option_trader.utils.gmail_notify import send_mail  

class site():

    def __init__(self, site_name):        

        self.site_name = site_name
        self.data_root = app_settings.DATA_ROOT_DIR        
        self.site_root = os.path.join(app_settings.SITE_ROOT_DIR, site_name)      
        self.user_root = os.path.join(self.site_root, app_settings.SITE_USER_DIR)       

        if os.path.exists(app_settings.DATA_ROOT_DIR) == False:
            os.mkdir(app_settings.DATA_ROOT_DIR)   

        if os.path.exists(app_settings.SITE_ROOT_DIR) == False:
            os.mkdir(app_settings.SITE_ROOT_DIR)  

        if os.path.exists(app_settings.CHART_ROOT_DIR) == False:
            os.mkdir(app_settings.CHART_ROOT_DIR)              

        if os.path.exists(app_settings.LOG_ROOT_DIR) == False:
            os.mkdir(app_settings.LOG_ROOT_DIR)      

        if os.path.exists(self.site_root) == False:
            os.mkdir(self.site_root)        

        if os.path.exists(self.user_root) == False:
            os.mkdir(self.user_root)           

        self.logger = logging.getLogger(__name__)

        if app_settings.DATABASES == 'sqlite3':
            try:                
                self.db_path = os.path.join(self.site_root,site_name+'_site.db')
                if os.path.exists(self.db_path ):
                    self.db_conn   = sqlite3.connect(self.db_path)  
                    self.default_strategy_list = self.get_default_strategy_list()
                    self.default_watchlist = self.get_default_watchlist()
                    self.default_notification_token = self.get_default_notification_token()                       
                else:
                    self.db_conn   = sqlite3.connect(self.db_path)  
                    cursor = self.db_conn.cursor()
                    cursor.execute("CREATE TABLE IF NOT EXISTS site_profile("+schema.site_profile+")")
                    cursor.execute("CREATE TABLE IF NOT EXISTS user_list("+schema.user_list+")")
                    cursor.execute("CREATE TABLE IF NOT EXISTS monitor("+schema.site_monitor_db+")")                                             
                    sql = "INSERT INTO site_profile (site_name, default_strategy_list, default_watchlist, default_notification_token) VALUES (?, ?, ?, ?)"              
                    self.default_strategy_list = app_settings.DEFAULT_SITE_STRATEGY_LIST
                    self.default_watchlist = app_settings.DEFAULT_SITE_WATCHLIST
                    self.default_notification_token = app_settings.DEFAULT_SITE_NOTIFICATION_TOKEN                 
                    cursor.execute(sql, [site_name, json.dumps(self.default_strategy_list), json.dumps(self.default_watchlist),self.default_notification_token])
                    self.db_conn.commit()    
                    self.expand_monitor_list(self.default_watchlist)
            except Exception as e:
                self.logger.exception(e)    
                raise e
        return

    def __enter__(self):
        return self
 
    def __exit__(self, *args):
        try:
            self.db_conn.close()
        except Exception as ex:
            self.logger.exception(ex)
            raise ex
                    
    def get_default_strategy_list(self):
        if app_settings.DATABASES == 'sqlite3':                 
            try:    
                sql = "SELECT default_strategy_list FROM site_profile"                
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.default_strategy_list =  json.loads(cursor.fetchone()[0])                
                return self.default_strategy_list
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error("sqlite3 only for now %s")
           
    def get_default_watchlist(self):
        if app_settings.DATABASES == 'sqlite3':                 
            try:    
                sql = "SELECT default_watchlist FROM site_profile"                
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.default_watchlist =  json.loads(cursor.fetchone()[0])                
                return self.default_watchlist
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error("sqlite3 only for now %s")

    def get_default_notification_token(self):
        if app_settings.DATABASES == 'sqlite3':                 
            try:    
                sql = "SELECT default_notification_token FROM site_profile"                
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.default_notification_token =  cursor.fetchone()[0]                
                return self.default_notification_token
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error("sqlite3 only for now %s")

    def update_default_strategy_list(self, strategy_list):

        if len(strategy_list) == 0:
            self.logger.error('Cannot set empty default strategy')
            return
        
        if app_settings.DATABASES == 'sqlite3':                 
            try:                              
                sql = "UPDATE site_profile SET default_strategy_list='"+json.dumps(strategy_list)+"' WHERE site_name='"+self.site_name+"'"                    
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.db_conn.commit()                 
                self.default_strategy_list = strategy_list
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error("sqlite3 only for now %s")

    def update_default_watchlist(self, watchlist):

        if len(watchlist) == 0:
            self.logger.error('Cannot set empty default watchlist')
            return
                
        if app_settings.DATABASES == 'sqlite3':                 
            try:                              
                sql = "UPDATE site_profile SET default_watchlist='"+json.dumps(watchlist)+"' WHERE site_name='"+self.site_name+"'"                    
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.db_conn.commit()                 
                self.default_watchlist = watchlist
                self.expand_monitor_list(watchlist)
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error("sqlite3 only for now %s")

    def update_default_notification_token(self, token):
                
        if app_settings.DATABASES == 'sqlite3':                 
            try:                              
                sql = "UPDATE site_profile SET default_notification_token='"+token+"' WHERE site_name='"+self.site_name+"'"                    
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.db_conn.commit()                 
                self.default_notification_token = token
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error("sqlite3 only for now %s")

    def expand_monitor_list(self, asset_list):
        if app_settings.DATABASES == 'sqlite3':                 
            monitor_list = self.get_monitor_list()
            cursor = self.db_conn.cursor()
            filter=[]               
            for symbol in asset_list:
                if symbol in monitor_list:
                    continue             
                #cursor.execute("CREATE TABLE IF NOT EXISTS monitor("+schema.site_monitor_db+")")                                             
                sql = "INSERT INTO monitor ("+asset.SYMBOL+") VALUES (?)"              
                try:
                    cursor.execute(sql, [symbol])
                    self.db_conn.commit()
                except Exception as e:                    
                    self.logger.warning('Add %s failed %s' % (symbol, str(e)))
                    continue
                filter.append(symbol)                
        else:
            self.logger.error("sqlite3 only for now %s")

        if len(filter) > 0:
            self.refresh_site_monitor_list(filter=filter)

    def get_monitor_list(self):
        if app_settings.DATABASES == 'sqlite3':                 
            try:    
                cursor = self.db_conn.cursor()                    
                symbols = [symbol[0] for symbol in cursor.execute("SELECT "+asset.SYMBOL+ " FROM monitor")]
                return symbols
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error("sqlite3 only for now %s")

    def get_monitor_df(self, filter=[]):
        if app_settings.DATABASES == 'sqlite3':                 
            try:    
                import pandas as pd                
                df = pd.read_sql_query("SELECT * FROM monitor", self.db_conn)                           
                df = df[df[asset.SYMBOL].isin(filter)] if len(filter)>0 else df           
                #df[asset.IV1] = pd.to_numeric(df[asset.IV1], errors='coerce')
                #df[asset.HV] = pd.to_numeric(df[asset.HV], errors='coerce')
                return df
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error("sqlite3 only for now %s")

    def refresh_site_monitor_list(self, filter=[]):    
        if app_settings.DATABASES == 'sqlite3':                 
            try:
                import pandas as pd                
                df = pd.read_sql_query("SELECT * FROM monitor", self.db_conn)                          
                refresh_monitor_list(df, filter=filter)                
                df.to_sql('monitor', self.db_conn, if_exists='replace', index=False)
                self.db_conn.commit()                
                return df
            except Exception as e:
                self.logger.exception(e)   
                raise e
                #return []
        else:
            self.logger.error("sqlite3 only for now %s")

    def select_high_IV_HV_ratio_asset(self, ratio, filter=[]):
        df = self.get_monitor_df(filter=filter)
        df[asset.IV1] = pd.to_numeric(df[asset.IV1], errors='coerce')
        df[asset.HV] = pd.to_numeric(df[asset.HV], errors='coerce')
        dd = df[df[asset.IV1]/df[asset.HV] >= ratio]
        return dd[asset.SYMBOL].to_list()  

    def select_low_IV_HV_ratio_asset(self, ratio, filter=[]):
        df = self.get_monitor_df(filter=filter)
        df[asset.IV1] = pd.to_numeric(df[asset.IV1], errors='coerce')
        df[asset.HV] = pd.to_numeric(df[asset.HV], errors='coerce')
        dd = df[df[asset.IV1]/df[asset.HV] <= ratio]
        return dd[asset.SYMBOL].to_list()  
    
    def create_user(self, user_name):        
        if user_name in self.get_user_list():
            self.logger.error('User %s already exists return existing user' % user_name)
            return user.user(self, user_name)
        
        if app_settings.DATABASES == 'sqlite3':        
            try:
                u = user.user(self, user_name)                
                sql = "INSERT INTO user_list VALUES (?,?)"       
                cursor = self.db_conn.cursor()
                cursor.execute(sql, [user_name, u.db_path]) 
                self.db_conn.commit()
                return u                
            except Exception as e:
                self.logger.exception(e)   
                return False
        else:
            self.logger.error('Unsupported database engine %s' % app_settings.DATABASES)

    def get_user(self, user_name):        
        if app_settings.DATABASES == 'sqlite3':        
            user_list = self.get_user_list()
            if user_name not in user_list:
                self.logger.error('User %s not found in this site' % user_name)
                return None                                                      
        else:
            self.logger.error('Unsupported database engine %s' % app_settings.DATABASES)

        return user.user(self, user_name=user_name)    
        
    def get_user_list(self):
        if app_settings.DATABASES == 'sqlite3':                
            try:
                cursor = self.db_conn.cursor()                    
                users = [name[0] for name in cursor.execute("SELECT user_name FROM user_list")]
                return users
            except Exception as e:
                self.logger.exception(e)   
                return []
        else:
            self.logger.error('Unsupported database engine %s' % app_settings.DATABASES)
            return []

    def publish_watchlist_report(self):

        user_name_list = self.get_user_list()

        for user_name in user_name_list:

            files = []

            user = self.get_user(user_name)

            to_addr = user.get_user_email()

            watchlist = user.get_default_watchlist()

            self.refresh_site_monitor_list(filter=watchlist)

            detail_df = self.get_monitor_df(filter=watchlist)

            #detail_df = mdf[mdf.symbol.isin(watchlist)]

            detail_df = detail_df[['symbol', 'last_price', '10d change%', '10d high', '10d low', 'support', 'resistence', 'trend', 'earning', 'forward_PE', 'rating', 'bb_pos', 'rsi', 'macd', 'mfi', 'HV', 'IV1%', 'IV2%', 'IV3%', 'IV4%']]

            detail_df.sort_values('10d change%', inplace=True)

            summary_df = detail_df[['symbol', 'last_price', '10d low', '10d high', '10d change%', 'earning', 'forward_PE', 'HV', 'IV1%', 'IV2%', 'IV3%', 'IV4%']]          

            today = str(datetime.now().date())

            report_path = os.path.join(user.report_dir, 'watchlist_report_'+today+'.csv')

            detail_df.to_csv(report_path, index=False)

            files.append(report_path)
            
            for symbol in watchlist:
                bng_path = os.path.join(app_settings.CHART_ROOT_DIR,symbol+'_BB.png')
                if os.path.exists(bng_path):
                    files.append(bng_path)
                else:
                    self.logger.error('BNG file %s not found' % bng_path)
        
            send_mail("jim.huang.bellevue@gmail.com", 
                        [to_addr], 
                        'Watchlist Update!! (' + ctime() + ')', 
                    "watchlist for %s" %user.user_name,
                    summary_df.to_html(index=False),             
                    files)
        
if __name__ == '__main__':

    site_name = 'mytest'

    import shutil

    site_path = app_settings.SITE_ROOT_DIR+'/'+site_name
    if os.path.exists(site_path):
        shutil.rmtree(site_path)

    mysite = site(site_name)
    strategy_list = mysite.get_default_strategy_list()
    mysite.update_default_strategy_list(strategy_list)
    watchlist = mysite.get_default_watchlist()
    mysite.expand_monitor_list(watchlist)
    monitor_list = mysite.get_monitor_list()
    monitor_df = mysite.get_monitor_df()
    mysite.update_default_watchlist(watchlist)
    token = mysite.get_default_notification_token()
    mysite.update_default_notification_token(token)                
    mysite.refresh_site_monitor_list(filter=[monitor_list[0]])  
    mysite.select_high_IV_HV_ratio_asset(1.0, filter=[monitor_list[0]])
    mysite.select_low_IV_HV_ratio_asset(1.0, filter=[monitor_list[0]])
    mysite.create_user('tester')
    mysite.get_user_list()
    mysite.get_user('tester')        

        

