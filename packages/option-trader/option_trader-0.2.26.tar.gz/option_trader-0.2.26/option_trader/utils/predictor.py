#import sys

#sys.path.append(r'\Users\jimhu\option_trader\src')    

import numpy as np
import math

from option_trader.consts import asset as at
from option_trader.consts import strategy as st
from option_trader.utils.calc_prob import predicted_list
from option_trader.utils.calc_prob import calc_prob_between

from option_trader.utils.data_getter import get_option_chain
from option_trader.utils.data_getter import get_price_history
from option_trader.utils.data_getter import get_option_exp_date

from option_trader.admin import quote

import logging

from option_trader.settings import app_settings    


def predict_price_range(symbol, target_date_list=[]):

    algo = app_settings.PRICE_RANGE_PREDICT_ALGO

    if algo == st.PRICE_RANGE_BY_RANDOM_WALK:
        return predict_price_range_with_prob_higher_than(symbol, target_date_list=target_date_list)

    if algo == st.PRICE_RANGE_BY_OPTION_STRADDLE: 
        return predict_price_range_by_straddle_option(symbol, target_date_list=target_date_list)

    if algo ==st.PRICE_RANGE_BY_LAST_NDAYS_RANGE : 
        return predict_price_range_by_last_ndays_price_range(symbol, target_date_list=target_date_list)

def predict_price_range_by_last_ndays_price_range(symbol, target_date_list=[]): 

    windows = app_settings.PREDICT_WINDOW

    from option_trader.utils.data_getter  import get_price_history

    hist = get_price_history(symbol)
    
    target_high = round(hist['Close'].rolling(window=windows).max().shift(1)[-1],2)

    target_low  = round(hist['Close'].rolling(window=windows).min().shift(1)[-1],2)   

    if len(target_date_list) == 0:
        target_date_list = get_option_exp_date(symbol)

    pred_list = {}

    for exp_date in target_date_list:
        predList = predicted_list(symbol, exp_date)
        win_prob =calc_prob_between(predList, target_high, target_low)            
        pred_list[exp_date] = {quote.HIGH:target_high, quote.LOW:target_low, quote.WIN_PROB:win_prob}

    pred_list['exp_date_list'] = target_date_list

    return pred_list
        
def predict_price_range_with_prob_higher_than(symbol, target_date_list=[]):

    if len(target_date_list) == 0:
        target_date_list = get_option_exp_date(symbol)

    target_prob = app_settings.TARGET_PROB

    pred_list = {}

    for target_date in target_date_list:

        predList = predicted_list(symbol, target_date)

        current_price = get_price_history(symbol)['Close'].iloc[-1]

        pert_step = 0.005

        target_high = current_price * (1+pert_step)
        
        target_low = current_price * (1-pert_step)

        total =  len(predList)

        while True:
            between = [i for i in predList if i >= target_low and i <= target_high]
            prob = (len(between)/(len(predList)))*100        
            if prob > target_prob:
                break
            target_high = target_high * (1+pert_step)    
            target_low = target_low * (1-pert_step)

        pred_list[target_date] = {quote.HIGH:target_high, quote.LOW:target_low, quote.WIN_PROB:target_prob}

    pred_list['exp_date_list'] = target_date_list

    return pred_list

def predict_price_range_by_straddle_option(symbol, target_date_list=[]): 

    target_prob = app_settings.TARGET_PROB

    if len(target_date_list) == 0:
        target_date_list = get_option_exp_date(symbol)

    call_chain = get_option_chain(symbol, at.CALL,  exp_date_list=target_date_list)

    put_chain =  get_option_chain(symbol, at.PUT, exp_date_list=target_date_list)

    current_price =get_price_history(symbol, period='1d', interval='1d')['Close'].iloc[-1]

    pred_list = {}

    pred_list['exp_date_list'] = []

    for exp_date in target_date_list:

        c = call_chain[call_chain[quote.EXP_DATE]==exp_date]

        p = put_chain[put_chain[quote.EXP_DATE]==exp_date]

        x = c[c[quote.STRIKE] > current_price]

        y = p[p[quote.STRIKE] > current_price]

        if x.shape[0] == 0 or y.shape[0] == 0:
            continue

        stradlle = x.iloc[0][quote.LAST_PRICE]+y.iloc[0][quote.LAST_PRICE]

        predList = predicted_list(symbol, exp_date)

        win_prob =calc_prob_between(predList, current_price+stradlle, current_price-stradlle)    

        #if win_prob < target_prob:
        #    continue

        pred_list['exp_date_list'].append(exp_date)

        pred_list[exp_date] = {quote.HIGH:current_price+stradlle, quote.LOW:current_price-stradlle, quote.WIN_PROB:win_prob}

    return pred_list

if __name__ == '__main__':

    #import sys

    #sys.path.append(r'\Users\jimhu\option_trader\src')

    from option_trader.utils.predictor import predict_price_range_by_straddle_option

    #predict_price_range('BLDR')


    x = predict_price_range_by_last_ndays_price_range('BLDR')

    print(x)

    print('-----------------------------')
    y = predict_price_range_by_straddle_option("BLDR")

    print(y)
    print('-----------------------------')

    z = predict_price_range_with_prob_higher_than('BLDR')

    print(z)