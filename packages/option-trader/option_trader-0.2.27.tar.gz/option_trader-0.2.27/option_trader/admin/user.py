
import pandas as pd
import os
import json   

from option_trader.settings import app_settings  as settings    
from option_trader.settings import schema as schema  

from option_trader.utils.line_norify import lineNotifyMessage 
from option_trader.admin.account import account
from option_trader.settings import app_settings
import re
import sqlite3

from json2html import *   

import logging

class user():  

    def __init__(self, site, user_name):
        
        self.site = site
        self.user_name = user_name
        self.email = ""
    
        self.logger = logging.getLogger(__name__)

        self.user_home_dir = os.path.join(site.user_root, self.user_name)        

        self.report_dir = os.path.join(self.user_home_dir, 'reports') 

        if os.path.exists(self.user_home_dir) == False:
            os.mkdir(self.user_home_dir)

        if os.path.exists(self.report_dir) == False:
            os.mkdir(self.report_dir)

        if settings.DATABASES == 'sqlite3':      

            self.db_path = os.path.join(self.user_home_dir,self.user_name+"_user.db")                     

            try:   
                if os.path.exists(self.db_path): 
                    self.db_conn  = sqlite3.connect(self.db_path)                   
                    self.email = self.get_user_email()
                    self.default_strategy_list = self.get_default_strategy_list()
                    self.default_watchlist = self.get_default_watchlist()
                    self.notification_token = self.get_notification_token()
                else:                                         
                    if os.path.exists(self.user_home_dir) == False:        
                        os.mkdir(self.user_home_dir)                    
                    self.default_strategy_list  = site.get_default_strategy_list()
                    self.default_watchlist      = site.get_default_watchlist()
                    self.notification_token     = site.get_default_notification_token()                
                    self.db_conn  = sqlite3.connect(self.db_path)  
                    cursor = self.db_conn.cursor()
                    cursor.execute("CREATE TABLE IF NOT EXISTS user_profile("+schema.user_profile+")")
                    cursor.execute("CREATE TABLE IF NOT EXISTS account_list("+schema.account_list+")")
                    #cursor.execute("CREATE TABLE IF NOT EXISTS watchlist("+schema.watchlist+")")                                             
                    sql = "INSERT INTO user_profile (name, email, default_strategy_list, default_watchlist, notification_token) VALUES (?, ?, ?, ?, ?)"                              
                    self.email = "askme@outlook.com"
                    cursor.execute(sql, [user_name, self.email, json.dumps(self.default_strategy_list), json.dumps(self.default_watchlist), self.notification_token])
                    self.db_conn.commit()                 
            except Exception as e:
                self.logger.error(e)       
                raise e
        else:
            self.logger.error('Unsupported database engine %s' % settings.DATABASES)

    def __enter__(self):
        return self
 
    def __exit__(self, *args):
        try:
            self.db_conn.close()
        except Exception as ex:
            self.logger.exception(ex)
            raise ex
                    
    # create new account        
    def get_user_profile(self):
        if settings.DATABASES == 'sqlite3':                 
            try:    
                sql = "SELECT email, default_strategy FROM user_profile"                
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                profile = cursor.fetchone()
                return profile[0], json.loads(profile[1]) 
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error("sqlite3 only for now %s")
        return None, None
    
    def get_default_strategy_list(self):
        if settings.DATABASES == 'sqlite3':                 
            try:    
                sql = "SELECT default_strategy_list FROM user_profile"                
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                return json.loads(cursor.fetchone()[0])                   
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error("sqlite3 only for now %s")
           
    def get_default_watchlist(self):
        if settings.DATABASES == 'sqlite3':                 
            try:    
                sql = "SELECT default_watchlist FROM user_profile"                
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                return json.loads(cursor.fetchone()[0])                   
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error("sqlite3 only for now %s")

    def get_notification_token(self):
        if settings.DATABASES == 'sqlite3':                 
            try:    
                sql = "SELECT notification_token FROM user_profile"                
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                return cursor.fetchone()[0]                   
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error("sqlite3 only for now %s")

    def get_user_email(self):
        if settings.DATABASES == 'sqlite3':                 
            try:    
                sql = "SELECT email FROM user_profile"                
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                return cursor.fetchone()[0]
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error("sqlite3 only for now %s")

    def update_default_strategy_list(self, strategy_list):
        if len(strategy_list) == 0:
            self.logger.error('Cannot set empty default strategy list')
            return [] 
              
        if settings.DATABASES == 'sqlite3':                 
            try:                              
                sql = "UPDATE user_profile SET default_strategy_list='"+json.dumps(strategy_list)+"' WHERE name='"+self.user_name+"'"                    
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
            self.logger.error('Cannot set empty default watchlist!')
            return []
        
        if settings.DATABASES == 'sqlite3':                 
            try:                              
                sql = "UPDATE user_profile SET default_watchlist='"+json.dumps(watchlist)+"' WHERE name='"+self.user_name+"'"                    
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.db_conn.commit()
                self.default_watchlist = watchlist         
                return watchlist        
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error("sqlite3 only for now %s")

    def update_notification_token(self, token):
            
        if len(token) != len(app_settings.LINE_NOTIFICATION_TOKEN):
            self.logger.error('Invalid notification token %s' %token)

        if settings.DATABASES == 'sqlite3':                 
            try:                              
                sql = "UPDATE user_profile SET notification_token='"+token+"' WHERE name='"+self.user_name+"'"                    
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.db_conn.commit()         
                self.notification_token = token
                return token        
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error("sqlite3 only for now %s")
            return ''

    def update_user_email(self, email):

        if len(email) == 0:
            return    
            
        if settings.DATABASES == 'sqlite3':                 
            try:                              
                sql = "UPDATE user_profile SET email='"+email+"' WHERE name='"+self.user_name+"'"                    
                cursor = self.db_conn.cursor()                    
                cursor.execute(sql)
                self.db_conn.commit()                 
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error("sqlite3 only for now %s")
                
    def create_account(self, account_name, initial_balance=app_settings.DEFAULT_ACCOUNT_INITIAL_BALANCE):       
        if settings.DATABASES == 'sqlite3':                
            try:
                account_list = self.get_account_list()
                if account_name in account_list:
                    self.logger.error('Account %s already exist return existing one' % account_name)
                    return account(self, account_name)
                
                a = account(self, account_name, initial_balance=initial_balance)             
                sql = "INSERT INTO account_list VALUES (?,?)"       
                cursor = self.db_conn.cursor()
                cursor.execute(sql, [account_name, a.db_path]) 
                self.db_conn.commit()
                return a
            except Exception as e:
                self.logger.exception(e)
                raise e     

    def get_account_list(self):
        if settings.DATABASES == 'sqlite3':                
            try:
                cursor = self.db_conn.cursor()                    
                account_name_list = [account_name[0] for account_name in cursor.execute("SELECT account_name FROM account_list")]
                return account_name_list
            except Exception as e:
                self.logger.exception(e)
                raise e
        else:
            self.logger.error('Unsupported database engine %s' % settings.DATABASES)

    def get_account(self, account_name):
        return account(self, account_name)
    
    def send_trade_report(self, account_name_list, trade_rec_list):

        if len(trade_rec_list) == 0:
            return

        to_addr = self.get_user_email()
        
        from time import ctime

        from option_trader.utils.gmail_notify import send_mail 

        import socket

        hostname = socket.gethostname()  

        send_mail("jim.huang.bellevue@gmail.com", 
                    [to_addr], 
                    'Trade Report!! ('+ ctime() + ') from ['+hostname+']', 
                    "Trade Report for " + self.user_name  + '|' + '.'.join(account_name_list) ,
                    json2html.convert(json = json.dumps(trade_rec_list)),             
                    [])


    def send_account_status_report(self):

        to_addr = self.get_user_email()
        
        from time import ctime

        from option_trader.utils.gmail_notify import send_mail 
        import option_trader.consts.strategy as st
        from option_trader.consts import asset

        from  option_trader.admin import position_summary
        import socket

        hostname = socket.gethostname()  

        account_list = self.get_account_list()

        if len(account_list)== 0:
            return
        
        history_df = pd.DataFrame()

        position_df = pd.DataFrame()

        for account_name in account_list:
            acct = self.get_account(account_name)
            acct.create_daily_account_summary()            
            init_balance = acct.get_initial_balance()
            d = acct.get_account_history().tail(1)
            e = acct.get_position_summary(status=asset.OPENED)
            e.insert(0, 'account name', account_name)
            d.insert(0, 'account name', account_name) 
            d.at[d.index[0], 'Gain %'] =  round(100 * (d.at[d.index[0], 'account value'] - init_balance)/ init_balance, 2)       
            history_df = pd.concat([history_df, d])
            position_df = pd.concat([position_df, e])

        history_summary = history_df[['account name', 'account value', 'asset value', 'cash position', 'margin position', 'Profit/Loss', 'Gain %' ]]

        mail_body = "<h3>Account Summary</h3>" + history_summary.to_html(index=False)

        monitor_df = self.site.get_monitor_df()[['symbol', 'last_price', '10d change%', '10d low', '10d high', 'IV1%', 'earning']]

        monitor_df['dist. to 10d high'] = monitor_df.apply(lambda x: (x['10d high']-x['last_price']) / (x['10d high']-x['10d low']), axis = 1) 

        stock_position = position_df[position_df[position_summary.STRATEGY] == st.UNPAIRED]
        if stock_position.shape[0] > 0:            
            mail_body += '<h3>Stock Positions</h3>'            
            account_list = stock_position['account name'].unique()                    
            for account_name in account_list:
                account_stock_position = stock_position[stock_position['account name']==account_name][[position_summary.SYMBOL, position_summary.QUANTITY, position_summary.LAST_STOCK_PRICE, position_summary.GAIN]]
                act = account_stock_position.merge(monitor_df)                
                act.sort_values('dist. to 10d high', inplace=True)
                stock_summary = act[[position_summary.SYMBOL, position_summary.QUANTITY, position_summary.GAIN, position_summary.LAST_STOCK_PRICE,  'dist. to 10d high', '10d change%', '10d low', '10d high', 'IV1%', 'earning']]
                stock_summary.columns  = [sub.replace('_', ' ') for sub in stock_summary.columns]
                mail_body += '<h3>'+account_name+'</h3>'+stock_summary.to_html(index=False) 

        option_position = position_df[position_df[position_summary.STRATEGY] != st.UNPAIRED] 
        if option_position.shape[0] > 0:
            mail_body += '<h3>Option Positions</h3>'            
            exp_date_list = option_position[position_summary.EXP_DATE].unique()
            exp_date_list.sort()
            for exp_date in exp_date_list:
                #option_summary = option_position[option_position[position_summary.EXP_DATE]==exp_date]
                option_summary = option_position[option_position[position_summary.EXP_DATE]==exp_date][['account name',position_summary.SYMBOL, position_summary.STRATEGY, position_summary.QUANTITY, position_summary.OPEN_PRICE, position_summary.LAST_PRICE,  position_summary.LAST_STOCK_PRICE, position_summary.BREAKEVEN_L, position_summary.BREAKEVEN_H, position_summary.GAIN, position_summary.LAST_WIN_PROB]]
                option_summary.sort_values(position_summary.GAIN, inplace=True)
                option_summary.columns  = [sub.replace('_', ' ') for sub in option_summary.columns]                
                mail_body += '<h3>'+exp_date+ '['+str(option_summary.shape[0])+']</h3>'+ option_summary.to_html(index=False)

        send_mail("jim.huang.bellevue@gmail.com", 
                    [to_addr], 
                    'Daily Account Satus Report!! ('+ ctime() + ') from ['+hostname+']', 
                    "Account Status for " + self.user_name ,
                    mail_body,      
                    [])
             

if __name__ == '__main__':

    from option_trader.admin.user import user              
    from option_trader.admin.site import site        

    mysite = site('mysite')
    #me = user(site=mysite, user_name='winwin')
    #me.send_account_status_report()
    me = user(site=mysite, user_name='chrishua')
    me.send_account_status_report()    
    #me.update_account('condor')
    #me.update_account('spread')