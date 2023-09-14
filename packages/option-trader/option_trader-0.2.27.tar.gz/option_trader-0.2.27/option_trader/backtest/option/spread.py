from tradeBot.backtest.option import strategy
from tradeBot.settings.tradeConfig import entryCrit
from tradeBot.settings.tradeConfig import exitCrit
from tradeBot.settings.tradeConfig import runtimeConfig
from tradeBot.settings.tradeConfig import marketCondition
from tradeBot.settings.tradeConfig import riskManager

from tradeBot.utils.optionTool import BSCallStrikeFromDelta
from tradeBot.utils.optionTool import BSPutStrikeFromDelta
from tradeBot.utils.optionTool import Spread
from tradeBot.utils.optionTool import time_to_maturity_in_year

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bt_spread')

class bt_spread(strategy.strategy):
    def __init__(self,
                 Type = 'Call',
                 Credit = True,
                 runtime_config = runtimeConfig(),
                 market_condition = marketCondition(),
                 risk_mgr = riskManager(),
                 entry_crit = entryCrit(),
                 exit_crit = exitCrit()): 
        super().__init__(runtime_config=runtime_config, 
                         market_condition=market_condition, 
                         risk_mgr = risk_mgr, 
                         entry_crit = entry_crit, 
                         exit_crit = exit_crit)

        self.Type = Type
        self.Credit = Credit
        self.risk_mgr.max_open_position = 1
        
    def get_name(self):
        if self.Credit == True:
            if self.Type == 'Call':
                return 'Credit Call Spread'
            else:
                return 'Credit Put Spread'
        else:
            if self.Type == 'Call':
                return 'Debit Call Spread'
            else:
                return 'Debit Put Spread'         

    def check_entry(self, i, dividend, trend):
                
        exp_date, sigma, trade_date, stock_price =  self.pre_check_entry(i, trend)      
        if exp_date == None:
            return
                        
        if self.Credit:
            if self.Type == 'Call':                    
                if trend.trend == 'increasing':
                    return                
                short_strike = BSCallStrikeFromDelta(stock_price, trade_date, exp_date, sigma=sigma, delta=self.entry_crit.max_delta_for_short)                
                if trend.trend == 'decreasing':
                    short_strike = short_strike - ( short_strike % self.runtime_config.spread)
                elif trend.trend == 'no trend':
                    short_strike = short_strike + ( short_strike % self.runtime_config.spread)        
                long_strike = short_strike + self.runtime_config.spread             
            else:
                if trend.trend == 'decreasing':
                    return                
                short_strike = BSPutStrikeFromDelta(stock_price, trade_date, exp_date, sigma=sigma, delta=self.entry_crit.max_delta_for_short)                
                if trend.trend == 'increasing':
                    short_strike = short_strike + ( short_strike % self.runtime_config.spread)
                elif trend.trend == 'no trend':
                    short_strike = short_strike - ( short_strike % self.runtime_config.spread)         
                long_strike = short_strike - self.runtime_config.spread           
            
        else: # Debit Spread
            if self.Type == 'Call':                
                if trend.trend == 'decreasing':
                    return                
                long_strike = BSCallStrikeFromDelta(stock_price, trade_date, exp_date, sigma=sigma, delta=self.entry_crit.min_delta_for_long)                
                if trend.trend == 'increasing':
                    long_strike = long_strike + ( long_strike % self.runtime_config.spread)
                elif trend.trend == 'no trend':
                    long_strike = long_strike - ( long_strike % self.runtime_config.spread)
                short_strike = long_strike + self.runtime_config.spread             
            else:
                if trend.trend == 'increasing':
                    return                
                long_strike = BSPutStrikeFromDelta(stock_price, trade_date, exp_date, sigma=sigma, delta=self.entry_crit.min_delta_for_long)                
                if trend.trend == 'decreasing':
                    long_strike = long_strike - ( long_strike % self.runtime_config.spread)
                elif trend.trend == 'no trend':
                    long_strike = long_strike + ( long_strike % self.runtime_config.spread)                
                short_strike = long_strike - self.runtime_config.spread
        
        spread = Spread(self.Type, exp_date, short_strike, long_strike)    
        fund_to_use = self.fund_alloc * self.risk_mgr.pos_max_alloc_pert
        spread.Open(stock_price, 
                    trade_date, 
                    fund_to_use, 
                    sigma, 
                    dividend)    
        
        if spread.Contract == 0: #fund not sufficient to open any position
            print('%s %s insuffient fund %.2f' % (self.get_name(), trade_date.strftime("%m-%d-%y"), fund_to_use))            
            return              

        self.confirm_order(i, spread, trend, exp_date)        
