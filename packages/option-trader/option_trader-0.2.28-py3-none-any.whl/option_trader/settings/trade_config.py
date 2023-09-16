
class entryCrit(object):
    def __init__(self, data=None):  
        if data != None:
            self.min_pnl = data['min_pnl']
            self.min_chance_of_win = data['min_chance_of_win']
            self.min_delta_for_long = data['min_delta_for_long']
            self.max_delta_for_short = data['max_delta_for_short']  
            self.max_slope = data['max_slope']            
            self.min_open_interest = data['min_open_interest']
            self.min_opt_vol = data['min_opt_vol']  
            self.min_IV_HV_ratio_for_short = data['min_IV_HV_ratio_for_short']       
            self.max_IV_HV_ratio_for_long = data['max_IV_HV_ratio_for_long']       
            self.max_rating = data['max_rating']
            self.covered_call_contract = data['covered_call_contract']       
            self.iron_condor_min_theta =data['iron_condor_min_theta']       
            self.min_price_to_short = data['min_price_to_short']
        else:
            self.min_pnl = 0.5
            self.min_chance_of_win = 50
            self.min_delta_for_long = 0.5
            self.max_delta_for_short = 0.5  
            self.max_slope = 0.3            
            self.min_open_interest = 100
            self.min_opt_vol = 1  
            self.min_IV_HV_ratio_for_short = 1.1       
            self.max_IV_HV_ratio_for_long = 0.9      
            self.max_rating = 2
            self.covered_call_contract = 1        
            self.iron_condor_min_theta = 0.5  
            self.min_price_to_short = 0.5            
        
import numpy as np
class marketCondition(object):
    def __init__(self, data=None):  
        if data != None:
            self.current_vix = data['current_vix']
            self.VIX_low = data['VIX_low'] 
            self.VIX_high = data['VIX_high']
            self.IV_Rank_low = data['IV_Rank_low']
            self.IV_Rang_high = data['IV_Rang_high']               
        else:
            self.current_vix = np.nan
            self.VIX_low = 20 
            self.VIX_high = 30
            self.IV_Rank_low = 20
            self.IV_Rang_high = 90            

class riskManager(object):
    def __init__(self, data=None):  
        if data != None: 
            self.stop_loss_percent = data['stop_loss_percent']
            self.stop_gain_percent = data['stop_gain_percent']
            self.close_days_before_earning = data['close_days_before_earning']
            self.close_days_before_expire = data['close_days_before_expire']
            self.open_min_days_to_earning = data['open_min_days_to_earning']        
            self.open_min_days_to_expire = data['open_min_days_to_expire']
            self.max_option_positions = data['max_option_positions']
            self.max_loss_per_position = data['max_loss_per_position']
            self.max_risk_per_asset = data['max_risk_per_asset']
            self.max_risk_per_expiration_date = data['max_risk_per_expiration_date']          
            self.weekly_stock_trade_amount = data['weekly_stock_trade_amount']              
            self.weekly_stock_trade_stop_percent = data['weekly_stock_trade_stop_percent']                 
        else:
            self.stop_loss_percent = 80
            self.stop_gain_percent = 90
            self.close_days_before_earning = 1
            self.close_days_before_expire = 1
            self.open_min_days_to_earning = 4        
            self.open_min_days_to_expire = 2
            self.max_option_positions = 10
            self.max_loss_per_position = 2500            
            self.max_risk_per_asset = 10
            self.max_risk_per_expiration_date = 10
            self.weekly_stock_trade_amount = 1000
            self.weekly_stock_trade_stop_percent = 10            
            
class runtimeConfig(object):
    def __init__(self, data=None):  
        if data != None:    
            self.init_balance = data['init_balance']           
            self.nweek = data['nweek'] 
            self.weekday = data['weekday']    
            self.trend_window_size = data['trend_window_size']         
            self.max_days_to_expire = data['max_days_to_expire']  
            self.max_spread = data['max_spread']  
            self.max_strike_ratio = data['max_strike_ratio']      
            self.max_bid_ask_spread = data['max_bid_ask_spread']
            self.auto_trade = data['auto_trade']
        else:
            self.init_balance = 100000           
            self.nweek = 0 
            self.weekday = 0    
            self.trend_window_size = 7        
            self.max_days_to_expire = 30
            self.max_spread = 10
            self.max_strike_ratio = 0.25
            self.max_bid_ask_spread = 3
            self.auto_trade = True


# weekday = 0: Monday
# nweek 0..N : number of weeks to expire
# stop_gain - profit taking percent
# stop_loss - stop loss percent

 