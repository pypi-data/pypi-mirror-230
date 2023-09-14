import pytest
import os
import shutil

from option_trader.admin.site import site
from option_trader.settings import app_settings
from option_trader.utils.line_norify import lineNotifyMessage

def test_site_creation():

    site_name = 'mytest'

    site_path = app_settings.SITE_ROOT_DIR+'/'+site_name
    if os.path.exists(site_path):
        shutil.rmtree(site_path)

    mysite = site(site_name)
    strategy_list = mysite.get_default_strategy_list()
    assert(len(strategy_list) > 0)
    mysite.update_default_strategy_list(strategy_list)
    watchlist = mysite.get_default_watchlist()
    assert(len(watchlist)> 0 )
    mysite.expand_monitor_list(watchlist)
    monitor_list = mysite.get_monitor_list()
    assert(len(monitor_list)>0)
    monitor_df = mysite.get_monitor_df()
    assert(monitor_df.shape[0] > 0)
    mysite.update_default_watchlist(watchlist)
    token = mysite.get_default_notification_token()
    mysite.update_default_notification_token(token)                
    #mysite.refresh_site_monitor_list(filter=[monitor_list[0]])  
    mysite.select_high_IV_HV_ratio_asset(1.0, filter=[monitor_list[0]])
    mysite.select_low_IV_HV_ratio_asset(1.0, filter=[monitor_list[0]])
    mysite.create_user('tester')
    user_list = mysite.get_user_list()
    assert('tester' in user_list)
    user = mysite.get_user('tester')   
    user.update_default_strategy_list(user.get_default_strategy_list())
    user.update_default_watchlist(user.get_default_watchlist()) 
    token = user.get_notification_token()
    user.update_notification_token(token)
    assert(lineNotifyMessage('test', token=token) == 200)        
    user.create_account('test_account')
    account_list = user.get_account_list()
    assert('test_account' in account_list)
    tc = user.get_account('test_account')
    tc.open_new_strategy_positions()

