import pandas as pd

import numpy as np
import uuid as UUID
from datetime import time, date, datetime, timedelta
from pytz import timezone
import json

import sys

sys.path.append(r'\Users\jimhu\option_trader\src')

from option_trader.admin    import position_summary
from option_trader.admin    import position
from option_trader.consts   import strategy
from option_trader.consts   import asset
from option_trader.settings import app_settings

from option_trader.utils.data_getter import get_price_history
from option_trader.utils.data_getter import get_next_earning_date
from option_trader.utils.calc_prob   import calc_prob_higher_than
from option_trader.utils.calc_prob   import calc_prob_lower_than
from option_trader.utils.calc_prob   import calc_prob_between
from option_trader.utils.calc_prob   import predicted_list

import logging

class optionLegDesc(object):
    def __init__(self, exp_date, strike, otype, open_action, quantity, price):
        self.STRIKE      = strike
        self.OTYPE       = otype
        self.OPEN_ACTION = open_action
        self.QUANTITY    = quantity
        self.EXP_DATE    = exp_date
        self.PRICE       = price

def map_fideliy_strategy(s, otype):

    logger = logging.getLogger(__name__)    
    
    if s == 'Unpaired':
        credit = False
        s = strategy.UNPAIRED
    elif s == 'Credit Spread':
        credit = True
        s = strategy.CREDIT_CALL_SPREAD if otype == asset.CALL else strategy.CREDIT_PUT_SPREAD
    elif s == 'Debit Spread':
        credit = False
        s = strategy.DEBIT_CALL_SPREAD if otype == asset.CALL else strategy.DEBIT_PUT_SPREAD        
    elif s == 'Short Iron Butterfly Spread':
        credit = True
        s = strategy.IRON_BUTTERFLY
    elif s == 'Short Iron Condor Spread':
        credit = True
        s = strategy.CREDIT_IRON_CONDOR
    elif s == 'Long Iron Condor Spread':
        credit = False
        s = strategy.DEBIT_IRON_CONDOR        
    elif s == 'Long Butterfly Spread':
        credit = False
        s = strategy.DEBIT_CALL_BUTTERFLY if otype == asset.CALL else strategy.DEBIT_PUT_BUTTERFLY 
    elif s == 'Short Butterfly Spread':
        credit = True
        s = strategy.CREDIT_CALL_BUTTERFLY if otype == asset.CALL else strategy.CREDIT_PUT_BUTTERFLY     
    elif s == 'Covered Call':
        credit = True
        s = strategy.COVERED_CALL
    elif s == 'Cash Covered Put':
        credit = True
        s = strategy.SHORT_PUT        
    elif s == 'Long Call':
        credit = False
        s = strategy.LONG_CALL       
    elif s == 'Long Put':
        credit = False
        s = strategy.LONG_PUT                  
    else:
        logger.error('Unhandled strategy %s' % s)
        
    return s, credit
        
def parse_expstrike(exp_strike):
    
    import re
    import datetime

    #print(exp_strike)
    x = re.split("\s", exp_strike)
    if len(x) < 4:
        print(exp_strike)
    otype = asset.CALL if x[4] == 'C' else asset.PUT
    strike = float(x[3])
    #exp_date = x[0]+' '+x[1]+' '+x[2]
    exp_date = datetime.datetime.strptime(x[0]+' '+x[1]+' '+x[2], '%b %d %Y').strftime('%Y-%m-%d')

    return otype, strike, exp_date

def save_to_db(account, total_cash, total_margin, summary_df, position_df):

    trade_date = str(datetime.now().astimezone(timezone(app_settings.TIMEZONE))) 

    symbol_list = summary_df[position.SYMBOL].unique()            

    for symbol in symbol_list:

        #stock_price = round(get_price_history(symbol, period='1d', interval='1d')['Close'][-1],2)        

        earning_date = str(get_next_earning_date(symbol))  

        sdf = summary_df[summary_df[position_summary.SYMBOL]==symbol]
        for i, rec in sdf.iterrows():
            uuid_value = rec[position_summary.UUID]
            symbol = rec[position_summary.SYMBOL]
            st = rec[position_summary.STRATEGY]
            credit = str(rec[position_summary.CREDIT])
            spread = rec[position_summary.SPREAD]
            open_price = rec[position_summary.OPEN_PRICE]
            exp_date = rec[position_summary.EXP_DATE]
            max_profit = rec[position_summary.MAX_PROFIT]
            max_loss = rec[position_summary.MAX_LOSS]
            margin = rec[position_summary.MARGIN]
            pnl = rec[position_summary.PNL]
            quantity = rec[position_summary.QUANTITY]
            status = rec[position_summary.STATUS]
            legs_desc = str(rec[position_summary.LEGS])

            win_prob = rec[position_summary.WIN_PROB]
            breakeven_h = rec[position_summary.BREAKEVEN_H]             
            breakeven_l = rec[position_summary.BREAKEVEN_L]

            if st == strategy.UNPAIRED:
                stock_price = open_price
            else:
                stock_price = np.nan

            fields = [uuid_value,symbol,st, credit,spread,\
                    round(open_price,2),exp_date,max_profit,max_loss,pnl,\
                    margin,quantity,status,legs_desc,trade_date,\
                    earning_date, round(stock_price,2), win_prob,breakeven_h, breakeven_l] 

            field_names =  "uuid, symbol, strategy, credit, spread, open_price, exp_date, max_profit, max_loss,pnl,margin,quantity,status,legs_desc,trade_date,earning_date,trade_stock_price, win_prob, breakeven_h, breakeven_l"

            values =  '?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?'                      

            sql = "INSERT INTO position_summary ("+field_names+") VALUES("+values+")" 
            cursor = account.db_conn.cursor()          
            cursor.execute(sql, fields)

    for i, rec in position_df.iterrows():

        symbol = rec[position.SYMBOL]
        if symbol in [asset.CASH, asset.MARGIN]:
            continue

        uuid_value = rec[position.UUID]
        leg_id = rec[position.LEG_ID]        
        symbol = rec[position.SYMBOL]
        otype = rec[position.OTYPE]        
        strike = rec[position.STRIKE]
        
        exp_date = rec[position.EXP_DATE]
        open_action = rec[position.OPEN_ACTION]
        quantity = rec[position.QUANTITY]
        open_price = round(rec[position.OPEN_PRICE],2)
        average_cost_basis = round(rec[position.AVERAGE_COST_BASIS],2)

        status = rec[position.STATUS]
        
        fields = [uuid_value, leg_id, symbol, otype, strike,\
                exp_date, open_action, quantity, open_price, average_cost_basis,\
                status, str(trade_date)]

        field_names = "uuid, leg_id, symbol, otype, strike,exp_date,open_action,quantity,open_price,average_cost_basis,status,trade_date"
        values =  '?,?,?,?,?,?,?,?,?,?,?,?' 
        sql = "INSERT INTO position ("+field_names+") VALUES("+values+")" 
        cursor = account.db_conn.cursor()          
        cursor.execute(sql, fields)

    account.update_cash_position(total_cash-total_margin)   
    
    account.update_margin_position(total_margin)
    
    account.db_conn.commit() 
        
def fidelity_reader(account, summary_file, position_df):

    logger = logging.getLogger(__name__)

    if account.get_position_summary().shape[0] > 0:
        logger.error('Can only import data onto empty account %s' % account.account_name)
        return False
    
    today = datetime.now(timezone(app_settings.TIMEZONE))
    
    summary_df =  pd.read_csv(summary_file)

    summary_df = summary_df[summary_df['Symbol'].notna()] 
    
    cash_df = position_df[(position_df['Symbol'].str.len() > 5) & (position_df['Symbol'].str.contains('-') == False)]
    
    total_cash1 = (cash_df['Current Value'].replace( '[\$,)]','', regex=True ).replace( '[(]','-', regex=True ).astype(float)).sum()
    
    total_cash2 = (cash_df['Last Price Change'].replace( '[\$,)]','', regex=True ).replace( '[(]','-', regex=True ).astype(float)).sum()

    total_cash = total_cash1+total_cash2

    total_margin = summary_df['Margin Requirements'].astype(float).sum()


    debit_pos = summary_df[summary_df['Quantity'].astype(float) > 0]

    credit_pos = summary_df[summary_df['Quantity'].astype(float) < 0]    

    total_debit = debit_pos['Averaged Cost'].astype(float).sum()

    total_credit = credit_pos['Averaged Cost'].astype(float).sum()

    init_balance = round(total_cash + total_margin + total_debit  -total_credit, 2) 

    account.set_initial_balance(init_balance)

    sdf = account.get_position_summary()
    
    pdf = account.get_positions()
    
    sindex = sdf.shape[0]
    
    pindex = pdf.shape[0]

    pair_list = summary_df['Pairing'].unique()  

    for pid in pair_list:            
        
        uuid_value = UUID.uuid4().hex   
        srow = summary_df[summary_df['Pairing']==pid]        
        symbol = srow.iloc[0]['Symbol']       
        
        sdf.at[sindex, position_summary.UUID] = uuid_value    
        sdf.at[sindex, position_summary.SYMBOL] = symbol
        fidelity_strategy = srow.iloc[0]['Strategy']
        srow['Margin Requirements'] = srow['Margin Requirements'].fillna(0)
        margin = float(srow['Margin Requirements'].astype(float).sum())        
        sdf.at[sindex, position_summary.MARGIN] = margin    
        sdf.at[sindex, position_summary.STATUS] = asset.OPENED      
        pdf.at[pindex, position.SYMBOL] = symbol
        
        if fidelity_strategy == 'Unpaired':                     
            quantity = srow.iloc[0]['Quantity'].astype(float)    
            if quantity < 1:
                continue            
            open_price = float(srow.iloc[0]['Averaged Cost']) / (quantity)            
            sdf.at[sindex, position_summary.STRATEGY] = strategy.UNPAIRED         
            sdf.at[sindex, position_summary.CREDIT] = False
            sdf.at[sindex, position_summary.QUANTITY] = quantity
            sdf.at[sindex, position_summary.OPEN_PRICE] = open_price 
            pdf.at[pindex, position.UUID]  = uuid_value                      
            pdf.at[pindex, position.OTYPE] = asset.STOCK
            pdf.at[pindex, position.QUANTITY] = quantity
            pdf.at[pindex, position.OPEN_PRICE] = open_price
            pdf.at[pindex, position.AVERAGE_COST_BASIS] = open_price            
            pdf.at[pindex, position.OPEN_ACTION] = asset.BUY_TO_OPEN        
            pdf.at[pindex, position.STATUS] = asset.OPENED     
            pdf.at[pindex, position.SCALE] = 1  
            pdf.at[pindex, position.LEG_ID] = 0 
            leg =  optionLegDesc("", np.nan, asset.STOCK, asset.BUY_TO_OPEN, quantity, open_price)
            sdf.at[sindex, position_summary.LEGS] = json.dumps([json.dumps(vars(leg))])        
            target_date = str(get_next_earning_date(symbol)) 
            
            if target_date == 'None':
                target_date = datetime.now() + timedelta(90)

            predList    = predicted_list(symbol, target_date) 

            win_prob  = calc_prob_higher_than(predList, open_price)

            sdf.at[sindex, position_summary.WIN_PROB] = win_prob
            sdf.at[sindex, position_summary.BREAKEVEN_L] = round(open_price,2)            
            sdf.at[sindex, position_summary.BREAKEVEN_H] = np.nan            
            pindex += 1     
        elif fidelity_strategy == 'Cash Covered Put':
            quantity = abs(srow.iloc[0]['Quantity'].astype(float))                
            open_price = float(srow.iloc[0]['Averaged Cost']) / (quantity*100)                      
            sdf.at[sindex, position_summary.STRATEGY] = strategy.SHORT_PUT         
            sdf.at[sindex, position_summary.CREDIT] = True
            sdf.at[sindex, position_summary.QUANTITY] = quantity
            sdf.at[sindex, position_summary.OPEN_PRICE] = open_price 
            sdf.at[sindex, position_summary.MAX_PROFIT] = open_price
            sdf.at[sindex, position_summary.MAX_LOSS] = np.nan
            sdf.at[sindex, position_summary.PNL] = np.nan           

            otype, strike, exp_date = parse_expstrike(srow.iloc[0]['Expiration & Strike'])        
            sdf.at[sindex, position_summary.EXP_DATE] = exp_date          

            leg  =  optionLegDesc(exp_date, strike, asset.PUT, asset.SELL_TO_OPEN, quantity, open_price)             
            sdf.at[sindex, position_summary.LEGS] = json.dumps([json.dumps(vars(leg))])  

            predList    = predicted_list(symbol, exp_date)    
            breakeven_l =  strike-open_price
            win_prob  = calc_prob_higher_than(predList, breakeven_l)            
            sdf.at[sindex, position_summary.WIN_PROB] = win_prob
            sdf.at[sindex, position_summary.BREAKEVEN_L] = breakeven_l            
            sdf.at[sindex, position_summary.BREAKEVEN_H] = np.nan   

            pdf.at[pindex, position.UUID]  = uuid_value                      
            pdf.at[pindex, position.OTYPE] = asset.PUT
            pdf.at[pindex, position.EXP_DATE] = exp_date
            pdf.at[pindex, position.STRIKE] = strike                
            pdf.at[pindex, position.QUANTITY] = quantity
            pdf.at[pindex, position.OPEN_PRICE] = open_price
            pdf.at[pindex, position.AVERAGE_COST_BASIS] = open_price            
            pdf.at[pindex, position.OPEN_ACTION] = asset.SELL_TO_OPEN        
            pdf.at[pindex, position.STATUS] = asset.OPENED     
            pdf.at[pindex, position.SCALE] = 1  
            pdf.at[pindex, position.LEG_ID] = 0 
            pindex += 1                
        elif fidelity_strategy in ['Long Call','Long Put']:
            quantity = abs(srow.iloc[0]['Quantity'].astype(float))                
            open_price = float(srow.iloc[0]['Averaged Cost']) / (quantity*100)                      
            sdf.at[sindex, position_summary.STRATEGY] = strategy.LONG_CALL         
            sdf.at[sindex, position_summary.CREDIT] = False
            sdf.at[sindex, position_summary.QUANTITY] = quantity
            sdf.at[sindex, position_summary.OPEN_PRICE] = open_price 
            sdf.at[sindex, position_summary.MAX_PROFIT] = np.nan
            sdf.at[sindex, position_summary.MAX_LOSS] = open_price
            sdf.at[sindex, position_summary.PNL] = np.nan           

            otype, strike, exp_date = parse_expstrike(srow.iloc[0]['Expiration & Strike'])
            sdf.at[sindex, position_summary.EXP_DATE] = exp_date    

            leg  =  optionLegDesc(exp_date, strike, asset.CALL, asset.BUY_TO_OPEN, quantity, open_price)             
            sdf.at[sindex, position_summary.LEGS] = json.dumps([json.dumps(vars(leg))])  

            predList    = predicted_list(symbol, exp_date)    

            breakeven_l =  round(strike+open_price, 2) if otype == asset.CALL else np.nan

            breakeven_h =  round(strike-open_price,2) if otype == asset.PUT else np.nan           

            win_prob  = calc_prob_higher_than(predList, breakeven_l) if otype == asset.CALL else  calc_prob_lower_than(predList, breakeven_h)          

            sdf.at[sindex, position_summary.WIN_PROB] = win_prob
            sdf.at[sindex, position_summary.BREAKEVEN_L] = breakeven_l            
            sdf.at[sindex, position_summary.BREAKEVEN_H] = breakeven_h  

            pdf.at[pindex, position.UUID]  = uuid_value                      
            pdf.at[pindex, position.OTYPE] = otype
            pdf.at[pindex, position.EXP_DATE] = exp_date
            pdf.at[pindex, position.STRIKE] = strike                
            pdf.at[pindex, position.QUANTITY] = quantity
            pdf.at[pindex, position.OPEN_PRICE] = open_price
            pdf.at[pindex, position.AVERAGE_COST_BASIS] = open_price            
            pdf.at[pindex, position.OPEN_ACTION] = asset.BUY_TO_OPEN        
            pdf.at[pindex, position.STATUS] = asset.OPENED     
            pdf.at[pindex, position.SCALE] = 1  
            pdf.at[pindex, position.LEG_ID] = 0 
            pindex += 1             
        elif fidelity_strategy == 'Covered Call':      
                            
            share =  srow[srow['Expiration & Strike'].str.contains(r'shares')]
            share_quantity = abs(share['Quantity'].min())
            share_cost = share['Averaged Cost'].astype(float).min() / (share_quantity)        
        
            call =  srow[~srow['Expiration & Strike'].str.contains(r'shares')]        
            call_quantity = abs(call['Quantity'].min())
            call_price = call['Averaged Cost'].astype(float).min() / (call_quantity * 100) 

            sdf.at[sindex, position_summary.QUANTITY] = call_quantity     
            sdf.at[sindex, position_summary.OPEN_PRICE] = round(call_price,2)      
            sdf.at[sindex, position_summary.STRATEGY] = strategy.COVERED_CALL 
            otype, strike, exp_date = parse_expstrike(call.iloc[0]['Expiration & Strike'])          

            predList    = predicted_list(symbol, exp_date)    
            breakeven_h =  round(strike-call_price,2)
            win_prob  = calc_prob_lower_than(predList, breakeven_h)
            sdf.at[sindex, position_summary.WIN_PROB] = win_prob
            sdf.at[sindex, position_summary.BREAKEVEN_L] = np.nan           
            sdf.at[sindex, position_summary.BREAKEVEN_H] = breakeven_h 
            sdf.at[sindex, position_summary.CREDIT] = True 
            sdf.at[sindex, position_summary.EXP_DATE] = exp_date         
         
            max_profit = abs(call_price)
            max_loss = share_cost - max_profit
            sdf.at[sindex, position_summary.MAX_PROFIT] = round(max_profit,2)
            sdf.at[sindex, position_summary.MAX_LOSS] = round(max_loss,2)
            sdf.at[sindex, position_summary.PNL] = round(max_profit/max_loss,2)        
        
            pdf.at[pindex, position.UUID]  = uuid_value        
            pdf.at[pindex, position.OTYPE] = asset.STOCK
            pdf.at[pindex, position.QUANTITY] = share_quantity
            pdf.at[pindex, position.OPEN_PRICE] = share_cost
            pdf.at[pindex, position.AVERAGE_COST_BASIS] = share_cost               
            pdf.at[pindex, position.STATUS] = asset.OPENED 
            pdf.at[pindex, position.OPEN_ACTION] = asset.BUY_TO_OPEN   
            pdf.at[pindex, position.SCALE] = 1  
            pdf.at[pindex, position.LEG_ID] = 0         
            pindex += 1

            pdf.at[pindex, position.SYMBOL]  = symbol            
            pdf.at[pindex, position.UUID]  = uuid_value        
            pdf.at[pindex, position.OTYPE] = asset.CALL
            pdf.at[pindex, position.EXP_DATE] = exp_date
            pdf.at[pindex, position.STRIKE] = strike                               
            pdf.at[pindex, position.QUANTITY] = call_quantity
            pdf.at[pindex, position.OPEN_PRICE] = call_price
            pdf.at[pindex, position.AVERAGE_COST_BASIS] = call_price               
            pdf.at[pindex, position.STATUS] = asset.OPENED 
            pdf.at[pindex, position.OPEN_ACTION] = asset.SELL_TO_OPEN   
            pdf.at[pindex, position.SCALE] = 1          
            pdf.at[pindex, position.LEG_ID] = 1                
            pindex += 1        

            stock_leg =  optionLegDesc("", np.nan, asset.STOCK, asset.BUY_TO_OPEN, share_quantity, share_cost)            
            call_leg  =  optionLegDesc(exp_date, strike, asset.CALL, asset.SELL_TO_OPEN, call_quantity, call_price)            

            sdf.at[sindex, position_summary.LEGS] = json.dumps([json.dumps(vars(stock_leg)), json.dumps(vars(call_leg))]) 

        else:
            otype, strike, exp_date = parse_expstrike(srow.head(1)['Expiration & Strike'].values[0])  
  
            option_trader_strategy, credit = map_fideliy_strategy(fidelity_strategy, otype)
            quantity = srow['Quantity'].abs().min()              
            sdf.at[sindex, position_summary.STRATEGY] = option_trader_strategy             
            sdf.at[sindex, position_summary.CREDIT] = credit
            sdf.at[sindex, position_summary.EXP_DATE] = exp_date          
            sdf.at[sindex, position_summary.QUANTITY] = quantity                  
            leg_id = 0            
            sdf.at[sindex, position_summary.LEGS] = [] 
            
            leg_desc = []
            for i, rec in srow.iterrows():
                otype, strike, exp_date = parse_expstrike(rec['Expiration & Strike'])                                      
                srow.at[i, position.STRIKE] = strike
                srow.at[i, position.OTYPE] = otype
                leg_quantity = rec['Quantity']
                open_action = asset.SELL_TO_OPEN if leg_quantity < 0 else asset.BUY_TO_OPEN
                srow.at[i, position.OPEN_ACTION]  = open_action
                open_price = abs(float(rec['Averaged Cost']) / (leg_quantity * 100))             
                pdf.at[pindex, position.OPEN_ACTION] = open_action         
                pdf.at[pindex, position.SYMBOL] = symbol
                pdf.at[pindex, position.UUID]  = uuid_value     
                pdf.at[pindex, position.STRIKE]  = strike              
                pdf.at[pindex, position.OTYPE] = otype            
                scale = abs(leg_quantity / quantity)
                srow.at[i, position.SCALE] = scale
                pdf.at[pindex, position.SCALE] = scale
                pdf.at[pindex, position.EXP_DATE] = exp_date                
                pdf.at[pindex, position.QUANTITY] = abs(leg_quantity)
                pdf.at[pindex, position.OPEN_PRICE] = open_price
                srow.at[i, 'price'] = open_price
                pdf.at[pindex, position.AVERAGE_COST_BASIS] = open_price                   
                pdf.at[pindex, position.STATUS] = asset.OPENED    
                pdf.at[pindex, position.LEG_ID] = leg_id
                leg =  optionLegDesc(exp_date, strike, otype, open_action, abs(leg_quantity), open_price)                
                leg_desc.append(json.dumps(vars(leg)))                                        
                                                                    
                leg_id += 1
                pindex += 1                

            sdf.at[sindex, position_summary.LEGS]  = json.dumps(leg_desc)   
            spread = srow['strike'].diff().abs().min()        
            srow['price'] = srow['Averaged Cost'].astype(float)  / (srow['Quantity'].astype(float) * 100) *  (srow['Quantity'].astype(float).abs() / quantity)
            open_price = abs(srow['price'].sum())            
            max_profit = open_price if credit else spread - open_price
            max_loss = spread - open_price if credit else open_price
            pnl = max_profit/max_loss        
            sdf.at[sindex, position_summary.SPREAD] = spread    
            sdf.at[sindex, position_summary.OPEN_PRICE] = round(open_price,2)                  
            sdf.at[sindex, position_summary.MAX_PROFIT] = round(max_profit,2)
            sdf.at[sindex, position_summary.MAX_LOSS]   = round(max_loss,2)        
            sdf.at[sindex, position_summary.PNL] = round(pnl,2)               

            win_prob = breakeven_h  = breakeven_l = np.nan
            
            today = datetime.now(timezone(app_settings.TIMEZONE))
            days_to_expire = (pd.Timestamp(exp_date).tz_localize(timezone(app_settings.TIMEZONE))-today).days                           
            
            if days_to_expire > 0:
                predList  = predicted_list(symbol, exp_date)    

            if srow.shape[0] == 2:
                sl = srow[srow[position.OPEN_ACTION] == asset.SELL_TO_OPEN]
                ll = srow[srow[position.OPEN_ACTION] == asset.BUY_TO_OPEN]
                sl_strike = sl.head(1)[position.STRIKE].values[0]
                ll_strike = ll.head(1)[position.STRIKE].values[0]
                if option_trader_strategy == strategy.CREDIT_PUT_SPREAD:
                    breakeven_l =sl_strike-open_price
                    breakeven_h = np.nan
                    if days_to_expire > 0:                    
                        win_prob = calc_prob_higher_than(predList, breakeven_l)    
                elif option_trader_strategy == strategy.DEBIT_PUT_SPREAD:             
                    breakeven_h =ll_strike - open_price
                    breakeven_l = np.nan
                    if days_to_expire > 0:                    
                        win_prob = calc_prob_lower_than(predList, breakeven_h) 
                elif option_trader_strategy == strategy.CREDIT_CALL_SPREAD:           
                    breakeven_h = sl_strike + open_price    
                    breakeven_l = np.nan
                    if days_to_expire > 0:                    
                        win_prob = calc_prob_lower_than(predList, breakeven_h)                         
                elif option_trader_strategy == strategy.DEBIT_CALL_SPREAD:
                    breakeven_l =ll_strike + open_price                 
                    breakeven_h = np.nan
                    if days_to_expire > 0:
                        win_prob = calc_prob_higher_than(predList, breakeven_l)   
                else:
                    logger.error('Unhandlered 2 legs strategy %s' % option_trader_strategy)                    

            elif srow.shape[0] == 4:
                psl = srow[(srow[position.OPEN_ACTION] == asset.SELL_TO_OPEN)  & (srow[position.OTYPE] == asset.PUT)] 
                pll = srow[(srow[position.OPEN_ACTION] == asset.BUY_TO_OPEN) & (srow[position.OTYPE] == asset.PUT)]
                csl = srow[(srow[position.OPEN_ACTION] == asset.SELL_TO_OPEN)  &(srow[position.OTYPE] == asset.CALL)] 
                cll = srow[(srow[position.OPEN_ACTION] == asset.BUY_TO_OPEN) & (srow[position.OTYPE] == asset.CALL)]
                psl_strike = psl.head(1)[position.STRIKE].values[0]
                pll_strike = pll.head(1)[position.STRIKE].values[0]
                csl_strike = csl.head(1)[position.STRIKE].values[0]
                cll_strike = cll.head(1)[position.STRIKE].values[0] 
                if option_trader_strategy == strategy.CREDIT_IRON_CONDOR:
                    breakeven_l = psl_strike - open_price
                    breakeven_h = csl_strike + open_price
                    if days_to_expire > 0:
                        win_prob = calc_prob_between(predList, breakeven_l, breakeven_h)                
                elif option_trader_strategy == strategy.DEBIT_IRON_CONDOR:
                    breakeven_h = cll_strike + max_loss
                    breakeven_l = pll_strike - max_loss
                    if days_to_expire > 0:          
                        win_prob = 100 - calc_prob_between(predList, breakeven_l, breakeven_h)                
                elif option_trader_strategy == strategy.IRON_BUTTERFLY:
                    breakeven_l = psl_strike - open_price
                    breakeven_h = csl_strike + open_price
                    if days_to_expire > 0:
                        win_prob = calc_prob_between(predList, breakeven_l, breakeven_h)                     
                elif option_trader_strategy == strategy.REVERSE_IRON_BUTTERFLY:
                    breakeven_h = cll_strike + max_loss
                    breakeven_l = pll_strike - max_loss
                    if days_to_expire > 0:          
                        win_prob = 100 - calc_prob_between(predList, breakeven_l, breakeven_h)
                else:
                    logger.error('Unhandlered 4 leg strategy %s' % option_trader_strategy)                       

            elif srow.shape[0] == 3:
                ml = srow[srow[position.SCALE] == 2] 
                ml_strike = ml.head(1)[position.STRIKE].values[0]
                ll = srow[(srow[position.SCALE] == 1) & (srow[position.STRIKE] < ml_strike)] 
                hl = srow[(srow[position.SCALE] == 1) & (srow[position.STRIKE] > ml_strike)] 
                ll_strike = ll.head(1)[position.STRIKE].values[0]
                hl_strike = hl.head(1)[position.STRIKE].values[0]

                if option_trader_strategy == strategy.CREDIT_CALL_BUTTERFLY:
                    breakeven_h = hl_strike  - open_price
                    breakeven_l = ll_strike  + open_price   
                    if days_to_expire > 0:                    
                        win_prob = 100-calc_prob_between(predList, breakeven_l, breakeven_h)   
                elif option_trader_strategy == strategy.CREDIT_PUT_BUTTERFLY:
                    breakeven_h = hl_strike - open_price
                    breakeven_l = ll_strike + open_price   
                    if days_to_expire > 0: 
                        win_prob = calc_prob_between(predList, breakeven_l, breakeven_h)   
                elif option_trader_strategy == strategy.DEBIT_CALL_BUTTERFLY:
                    breakeven_h = hl_strike - open_price
                    breakeven_l = ll_strike + open_price
                    if days_to_expire > 0:   
                        win_prob = 100-calc_prob_between(predList, breakeven_l, breakeven_h)                         
                elif option_trader_strategy == strategy.DEBIT_PUT_BUTTERFLY:
                    breakeven_h = hl_strike - open_price
                    breakeven_l = ll_strike + open_price
                    if days_to_expire > 0:     
                        win_prob = 100-calc_prob_between(predList, breakeven_l, breakeven_h)                       
                else:
                    logger.error('Unhandlered 3 leg strategy %s' % option_trader_strategy)
            else:
                logger.error('Unhandlered %d legs strategy %s' % (srow.shape[0], option_trader_strategy))                

            sdf.at[sindex, position_summary.WIN_PROB] = win_prob
            sdf.at[sindex, position_summary.BREAKEVEN_H] = round(breakeven_h,2)            
            sdf.at[sindex, position_summary.BREAKEVEN_L] = round(breakeven_l,2)

        sindex += 1
        
    save_to_db(account, total_cash, total_margin, sdf, pdf)

    return True

import os

def import_fidelity_pofolio(user, profolio_file_name):
    logger = logging.getLogger(__name__)
    position_file_path = user.user_home_dir+'/dataset/fidelity/' + profolio_file_name
    if os.path.exists(position_file_path) == False:
        logger.error('File %s not found' % position_file_path)
        return

    portfolio_df = pd.read_csv(position_file_path)
    portfolio_df = portfolio_df[portfolio_df ['Symbol'].notna()]         
    account_number_list = portfolio_df['Account Number'].unique()     

    monitor_list = []

    for account_number in account_number_list:
        summary_file_path = user.user_home_dir+'/dataset/fidelity/Option_Summary_for_Account_'+account_number+'.csv'
        if os.path.exists(summary_file_path):

            account_position = portfolio_df[portfolio_df['Account Number'] == account_number]            
            account_name = account_position.head(1)['Account Name'].values[0] + ' (' + account_number +')'           
            account_obj = user.create_account(account_name)            
        
            print('processing %s' % summary_file_path)

            account_position_df = portfolio_df[portfolio_df['Account Number'] == account_number]

            fidelity_reader(account_obj, summary_file_path, account_position_df)

            rt = account_obj.get_default_runtime_config()
            rt.auto_trade = False
            account_obj.update_default_runtime_config(rt)

            sdf = account_obj.get_position_summary()

            symbol_list = list(sdf[position_summary.SYMBOL].unique())              
            
            account_obj.update_default_watchlist(symbol_list)

            monitor_list += symbol_list
            
            account_obj.update_position()
        else:
            print('summary file %s not found' %  summary_file_path)

    monitor_list = list(set(monitor_list))

    mysite.expand_monitor_list(monitor_list)

if __name__ == '__main__':

    from option_trader.admin.site import site
    from option_trader.admin.user import user
    from option_trader.consts import strategy

    mysite = site('mysite')

    chrishua = mysite.create_user('chrishua')

    jihuang = mysite.create_user('jihuang')    

    #import_fidelity_pofolio(chrishua, 'Portfolio_Positions.csv')

    import_fidelity_pofolio(chrishua, 'Portfolio_Positions.csv')

    #chrishua_position_file = 'C:\\Users\\jimhu\\option_trader\\data\\dataset\\fidelity\\chrishua_185173665_position.csv'
    #chrishua_summary_file = 'C:\\Users\\jimhu\\option_trader\\data\\dataset\\fidelity\\chrishua_185173665_summary.csv'

    #tira = chrishua.create_account('RolloverIRA')
    #sdf = fidelity_reader(tira, chrishua_summary_file, chrishua_position_file)

    #jihuang = mysite.create_user('jihuang')
    #tira = jihuang.create_account('TranditionalIRA')

    #sdf = fidelity_reader(tira, summary_file, position_file)