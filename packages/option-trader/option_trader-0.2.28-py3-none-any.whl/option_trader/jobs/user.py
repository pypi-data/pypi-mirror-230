import sys

sys.path.append(r'\Users\jimhu\option_trader\src')

from option_trader.jobs import core
from option_trader.admin.site    import site
from option_trader.admin.user    import user
from option_trader.admin.account import account
from option_trader.utils.line_norify import lineNotifyMessage

import logging

from option_trader.settings import app_settings    

class user_account_position_update_job():

    def __init__(self, site_name, user_name):     
        self.site_name = site_name
        self.user_name = user_name
        return
    
    def execute(self):        
        with site(self.site_name) as mysite:
            trade_rec_list = []
            with user(user_name=self.user_name, site=mysite) as this_user:
                account_list = this_user.get_account_list()
                for account_name in account_list:
                    this_account = this_user.get_account(account_name)
                    trade_rec_list += this_account.update_position()
                if len(trade_rec_list) > 0:
                   this_user.send_trade_report(account_list, trade_rec_list) 
                   import socket
                   hostname = socket.gethostname()               
                   msg = "[%s|%s] %d transactions created in user account update job run" % (hostname, self.user_name, len(trade_rec_list))
                   lineNotifyMessage( msg, this_user.notification_token)                    
        return 
       
class user_account_trade_job():

    def __init__(self, site_name, user_name):     
        self.site_name = site_name
        self.user_name = user_name
        return
    def execute(self):
        
        with site(self.site_name) as mysite:            
            with user(user_name=self.user_name, site=mysite) as this_user:
                trade_rec_list = []
                account_list = this_user.get_account_list()
                for account_name in account_list:
                    this_account = this_user.get_account(account_name)
                    trade_rec_list += this_account.open_new_strategy_positions()    
                if len(trade_rec_list) > 0:
                    this_user.send_trade_report(account_list, trade_rec_list)
                    import socket
                    hostname = socket.gethostname()                       
                    msg = "[%s|%s] %d transactions created in account trade job run" % (hostname, self.user_name, len(trade_rec_list))
                    lineNotifyMessage( msg, this_user.notification_token)                      
        return


if __name__ == '__main__':
    
    from logging.handlers import RotatingFileHandler
    
    FORMAT = '%(asctime)s-%(levelname)s (%(message)s) %(filename)s-%(lineno)s-%(funcName)s'
        
    ch = logging.StreamHandler()    
    #ch.setFormatter(formatter)

    import os

    if os.path.exists(app_settings.LOG_ROOT_DIR) == False:        
        os.mkdir(app_settings.LOG_ROOT_DIR)

    import datetime    
    daily_log_path = app_settings.LOG_ROOT_DIR+'\\my_log-'+datetime.date.today().strftime("%Y-%m-%d")+'.log'
    fh = RotatingFileHandler(daily_log_path)
    #fh.setFormatter(formatter)

    logging.basicConfig(
                level=logging.INFO,
                format=FORMAT,
                handlers=[ch, fh]
            )

    logger = logging.getLogger(__name__)

    # Filter paramiko.transport debug and info from basic logging configuration
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARN)

    logging.getLogger('yfinance').setLevel(logging.WARN)


    #print('trade winwin account')
    #t =  user_account_trade_job('mysite', 'winwin')
    #t.execute()

    
    #print('UPDATE winwin account')
    #t =  user_account_position_update_job('mysite', 'winwin')
    #t.execute()

    #logger.debug('processing single')
    #t =  trade('mysite', 'jihuang', 'single')
    #t.execute()

    #print('update stester account positions')
    #t =  update_user_account_position('mysite', 'jihuang')
    #t.execute()

    #print('trade ')
    #t =  trade_user_account('mysite', 'stester')
    #t.execute()

    #print('trade RolloverIRA')
    #t =  trade_user_account('mysite', 'chrishua')
    #t.execute()

    print('update account position')
    t =  user_account_position_update_job('mysite', 'chrishua')
    t.execute()

    #print('trade spread')    
    #t=  trade('mysite', 'jihuang', 'spread')
    #t.execute()

    #print('processing user account for jihuang')
    #t =  trade_user_account('mysite', 'chrishua')
    #t.execute()

    #print('processing butterfly')
    #t =  trade('mysite', 'jihuang', 'butterfly')
    #t.execute()

    #print('update butterfly')
    #t =  update_position('mysite', 'jihuang', 'butterfly')
    #t.execute()


    #print('processing single')
    #t =  update_position('mysite', 'jihuang', 'single')
    #t.execute()

    #print('processing spread')    
    #t=  update_position('mysite', 'jihuang', 'spread')
    #t.execute()


    #print('processing iron_condor')
    #t =  update_position('mysite', 'jihuang', 'iron_condor')
    #t.execute()

