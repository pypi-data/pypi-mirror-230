import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import time, date, datetime, timedelta
from pytz import timezone

import pandas_market_calendars as mcal
nyse = mcal.get_calendar('NYSE')

#import sys
#sys.path.append(r'\Users\jimhu\option_trader\src')    

from option_trader.settings import app_settings

import logging

from diskcache import Cache

pl_cache = Cache()

def highest_price_with_prob_low_than(predList, current_price, prob):

    target_price = current_price
    prob = prob/100
    while True:
        over = [i for i in predList if i > target_price]            
        less = [i for i in predList if i <= target_price]
        if len(less)/(len(less)+len(over)) > prob:
            target_price -= 0.5
        else:
            return target_price
        
def calc_prob_higher_than(predList, target_price):

    over = [i for i in predList if i >= target_price]
    prob = (len(over)/(len(predList))) * 100
    return round(prob,2)    
               
def calc_prob_lower_than(predList, target_price):
    less = [i for i in predList if i < target_price]      
    prob = (len(less)/(len(predList))) * 100    
    return round(prob,2)

def calc_prob_between(predList, target_price_1, target_price_2):
    if target_price_1 > target_price_2:           
        target_price_LOW = target_price_2
        target_price_HIGH = target_price_1
    else:
        target_price_LOW = target_price_1
        target_price_HIGH = target_price_2
        
    between = [i for i in predList if i >= target_price_LOW and i <= target_price_HIGH]    #outside = [i for i in predList if i < target_price_LOW or i > target_price_HIGH] 

    prob = (len(between)/(len(predList)))*100
        
    return round(prob,2)

def predicted_list(symbol, target_date, iterations=1000):

    logger = logging.getLogger(__name__)
    
    cache_key =symbol+'pred_list'+str(target_date)
    #logger.info('predicted list key %s' % (cache_key))    
    if cache_key in pl_cache:     
        #logger.info('hit %s' % cache_key)   
        try:
            return pl_cache[cache_key]
        except:
            pass

    #logger.info('predicted list key %s' % (cache_key))    

    data = pd.DataFrame()

    from option_trader.utils.data_getter  import get_price_history
    
    quote = get_price_history(symbol)

    data[symbol] = quote['Close']

    #logger.debug("predicted_list %s", symbol)
    """
        This function calculated the probability of a stock being above a certain threshhold, which can be defined as a value (final stock price) or return rate (percentage change)
        Input: 
        1. symbol: specific ticker to compute probability fo
        2. target_date: some future date
        Output:
        simulated predicted list

    """
    def log_returns(data):
        #logger.debug("log_returns")
        return (np.log(1+data.pct_change()))

    def simple_returns(data):
        #logger.debug("simple_returns")            
        return ((data/data.shift(1))-1)

    def drift_calc(data, return_type='log'):
        #logger.debug("drift_calc")    
        if return_type=='log':
            lr = log_returns(data)
        elif return_type=='simple':
            lr = simple_returns(data)
        u = lr.mean()
        var = lr.var()
        drift = u-(0.5*var)
        try:
            return drift.values
        except:
            return drift

    def daily_returns(data, days, iterations, return_type='log'):
        #logger.debug("daily_returns")  
        ft = drift_calc(data, return_type)
        if return_type == 'log':
            try:
                stv = log_returns(data).std().values
            except Exception as e:
                logger.exception(e)                            
                stv = log_returns(data).std()
        elif return_type=='simple':
            try:
                stv = simple_returns(data).std().values
            except Exception as e:
                logger.exception(e)    
                stv = simple_returns(data).std()    
            #Oftentimes, we find that the distribution of returns is a variation of the normal distribution where it has a fat tail
            # This distribution is called cauchy distribution
        
        dr = np.exp(ft + stv * norm.ppf(np.random.rand(days, iterations)))
        
        return dr

    def num_of_trade_days(end_date):         
        #nyse = mcal.get_calendar('NYSE')        
        today = str(datetime.now(timezone(app_settings.TIMEZONE)).date())
        schedule = nyse.schedule(start_date=today, end_date=end_date)
        return schedule.shape[0]
    
    trade_days = num_of_trade_days(target_date)

    # Generate daily returns
    returns = daily_returns(data, trade_days, iterations)

    # Create empty matrix
    price_list = np.zeros_like(returns)
    # Put the last actual price in the first row of matrix. 
    try: #????
        price_list[0] = data.iloc[-1]
    except Exception as e:
        logger.exception(e)
        logger.error('symbol ' +symbol)      
        logger.error('trade days ' + str(trade_days))       
        logger.error('target date ' + str(target_date))             
        #logger.error(target_date)
        logger.error(returns)

    # Calculate the price of each day
    if trade_days == 0:
        return []

    for t in range(1,trade_days):
        price_list[t] = price_list[t-1]*returns[t]


    predicted = pd.DataFrame(price_list)
    predicted = predicted.iloc[-1]
    predList = predicted.tolist()

    pl_cache.set(cache_key, predList, expire=24*60^60)

    return predList

def calc_win_prob(symbol, exp_date, strategy, breakeven_l, breakeven_h):

    logger = logging.getLogger(__name__)

    from option_trader.consts import strategy as st

    predList    = predicted_list(symbol, exp_date)    

    if strategy == st.CREDIT_IRON_CONDOR:
        return calc_prob_between(predList, breakeven_l, breakeven_h)
    elif strategy == st.DEBIT_IRON_CONDOR:
        return 100-calc_prob_between(predList, breakeven_l, breakeven_h)    
    elif strategy == st.CREDIT_PUT_SPREAD:
        return calc_prob_higher_than(predList, breakeven_l)            
    elif strategy == st.DEBIT_PUT_SPREAD:
        return calc_prob_lower_than(predList, breakeven_h) 
    elif strategy == st.CREDIT_CALL_SPREAD:    
        return  calc_prob_lower_than(predList, breakeven_h)
    elif strategy == st.DEBIT_CALL_SPREAD:                
        return calc_prob_higher_than(predList, breakeven_l)   
    elif strategy == st.LONG_CALL:
        return calc_prob_higher_than(predList, breakeven_l)             
    elif strategy == st.COVERED_CALL:
        return calc_prob_lower_than(predList, breakeven_h)          
    elif strategy == st.LONG_PUT:
        return calc_prob_lower_than(predList, breakeven_h)           
    elif strategy == st.SHORT_PUT:
        return calc_prob_higher_than(predList, breakeven_l)        
    elif strategy == st.DEBIT_CALL_BUTTERFLY:
        return calc_prob_between(predList, breakeven_l, breakeven_h)     
    elif strategy == st.CREDIT_CALL_BUTTERFLY:
        return 100-calc_prob_between(predList, breakeven_l, breakeven_h)
    elif strategy == st.CREDIT_PUT_BUTTERFLY:             
        return 100 - calc_prob_between(predList, breakeven_l, breakeven_h)     
    elif strategy == st.DEBIT_PUT_BUTTERFLY:    
        return calc_prob_between(predList, breakeven_l, breakeven_h) 
    elif strategy == st.REVERSE_IRON_BUTTERFLY: 
        return 100-calc_prob_between(predList, breakeven_l, breakeven_h)  
    elif strategy  == st.IRON_BUTTERFLY:    
        return calc_prob_between(predList, breakeven_l, breakeven_h)     
    else:
        logger.error('Unknown strategy %s' % strategy)
        return np.nan

if __name__ == '__main__':
    
    from option_trader.utils.data_getter  import get_price_history
    
    symbol='AAPL'
    quote = get_price_history(symbol)
