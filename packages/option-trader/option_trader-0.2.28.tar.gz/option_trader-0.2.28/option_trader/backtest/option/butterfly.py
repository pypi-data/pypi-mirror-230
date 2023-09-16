from tradeBot.backtest.option import strategy
from tradeBot.settings.tradeConfig import entryCrit
from tradeBot.settings.tradeConfig import exitCrit
from tradeBot.settings.tradeConfig import runtimeConfig
from tradeBot.settings.tradeConfig import marketCondition
from tradeBot.settings.tradeConfig import riskManager

from tradeBot.utils.optionTool import Spread

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bt_butterfly')

class bt_butterfly(strategy.strategy):
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
        self.risk_mgr.max_open_position = 2  

    def get_name(self):
        if self.Credit == True:
            if self.Type == 'Call':
                return 'Credit Call Butterfly'
            elif self.Type == 'Put':
                return 'Credit Put Butterfly'
            elif self.Type == 'Iron':
                return 'Iron Butterfly'            
        else:
            if self.Type == 'Call':
                return 'Debit Call Butterfly'
            elif self.Type == 'Put':
                return 'Debit Put Butterfly' 
            elif self.Type == 'Iron':
                return 'Reverse Iron Butterfly'
            
    def report(self):
        print('%s : win/total count %.1f/%.1f gain %.2f%%' % 
            (self.get_name(), self.perf_counter.win_count/2, self.perf_counter.count/2, 100 * (self.perf_counter.profit/self.risk_mgr.init_fund_alloc)))
            
            
    def check_entry(self, i, dividend, trend):
        
        exp_date, sigma, trade_date, stock_price =  self.pre_check_entry(i, trend)      
        if exp_date == None:
            return
        
        fund_to_use = self.fund_alloc * self.risk_mgr.pos_max_alloc_pert
        
        if trend.trend == 'increasing' or trend.trend == 'decreasing':
            if abs(trend.slope) > self.entry_crit.max_slope:
                return
        
        low_strike = stock_price - self.runtime_config.spread
        high_strike = stock_price + self.runtime_config.spread
        mid_strike = stock_price            
        fund_to_use =  fund_to_use /2         
        
        if self.Credit:
            if self.Type == 'Call' or self.Type == 'Put':
                lower_spread = Spread(self.Type, exp_date, low_strike, mid_strike)
                higher_spread = Spread(self.Type, exp_date, high_strike, mid_strike)
            elif self.Type == 'Iron':
                lower_spread = Spread('Put', exp_date, mid_strike, low_strike)
                higher_spread = Spread('Call', exp_date, mid_strike, high_strike)               
        else: # Debit
            if self.Type == 'Call' or self.Type == 'Put':            
                lower_spread = Spread(self.Type, exp_date, mid_strike, low_strike)
                higher_spread = Spread(self.Type, exp_date, mid_strike, high_strike)
            elif self.Type == 'Iron': #reverse Iron Butterfly                
                # For example, if a stock is trading at $100, a bull call spread could be 
                # entered by purchasing a $100 call and selling a $110 call. 
                # A bear put spread could be entered by purchasing a $100 put and selling 
                # a $90 put. 
                higher_spread = Spread('Call', exp_date, high_strike, mid_strike)                
                lower_spread = Spread('Put', exp_date, low_strike, mid_strike)

                
        lower_spread.Open(stock_price, trade_date, fund_to_use, sigma, dividend)           
        higher_spread.Open(stock_price, trade_date, fund_to_use, sigma, dividend)  
        
        if lower_spread.Contract == 0 or higher_spread.Contract == 0:
            logger.debug('butterfly %s insuffient fund %.2f' % (trade_date.strftime("%m-%d-%y"), fund_to_use))            
            return 
        
        contract = min(lower_spread.Contract, higher_spread.Contract)        
        lower_spread.Contract = contract
        higher_spread.Contract = contract
                
        if self.confirm_order(i, lower_spread, trend, exp_date):        
            if self.confirm_order(i, higher_spread, trend, exp_date) == False:
                logger.debug("Cannot establish butterfly position")                
                self.Open_Positions.pop() 
                