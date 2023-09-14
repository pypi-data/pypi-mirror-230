from tradeBot.backtest.option import strategy
from tradeBot.settings.tradeConfig import entryCrit
from tradeBot.settings.tradeConfig import exitCrit
from tradeBot.settings.tradeConfig import runtimeConfig
from tradeBot.settings.tradeConfig import marketCondition
from tradeBot.settings.tradeConfig import riskManager

from tradeBot.utils.optionTool import BSCallStrikeFromDelta
from tradeBot.utils.optionTool import BSPutStrikeFromDelta
from tradeBot.utils.optionTool import Spread

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bt_credit_iron_condor')

'''
An iron condor consists of selling an out-of-the-money bear call credit spread above the stock price 
and an out-of-the-money bull put credit spread below the stock price with the same expiration date. 

The strategy looks to take advantage of a drop in volatility, time decay, 
and little or no movement from the underlying asset. Iron condors are essentially a 
short strangle with long option protection purchased above and below the short strikes 
to define risk.

https://optionalpha.com/strategies/iron-condor

'''
class bt_credit_iron_condor(strategy.strategy):
    def __init__(self,
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
        self.breakeven_high = 0
        self.breakeven_low = 0
        self.risk_mgr.max_open_position = 4
      
    def get_name(self):
        return 'short iron condor'    
    
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
                logger.debug('trend slope %.2f greater than max_slope %.2f' % 
                         (trend.slope, self.entry_crit.max_slope))    
                #print('trend slope %.2f greater than max_slope %.2f' % 
                #         (trend.slope, self.entry_crit.max_slope))                   
                return
            
        if self.market_condition.current_vix < self.market_condition.VIX_low or self.market_condition.current_vix > self.market_condition.VIX_high:
            logger.debug('vix %.2f out of range low %.2f high %.2f' %
                 (self.market_condition.current_vix, self.market_condition.VIX_low, self.market_condition.VIX_high))
                
            #print('vix %.2f out of range low %.2f high %.2f' %
            #     (self.market_condition.current_vix, self.market_condition.VIX_low, self.market_condition.VIX_high))
            return 
        
        put_short_strike = BSPutStrikeFromDelta(stock_price, trade_date, exp_date, sigma=sigma, delta=self.entry_crit.max_delta_for_short)                                                                    
        put_short_strike = put_short_strike + ( put_short_strike % self.runtime_config.spread)
        call_short_strike = BSCallStrikeFromDelta(stock_price, trade_date, exp_date, sigma=sigma, delta=self.entry_crit.max_delta_for_short)                                                                    
        call_short_strike = call_short_strike + ( call_short_strike % self.runtime_config.spread)            
        put_long_strike = put_short_strike - self.runtime_config.spread
        call_long_strike = call_short_strike + self.runtime_config.spread
        fund_to_use =  fund_to_use /2 
                                           
        Put_Spread = Spread('Put', exp_date, put_short_strike, put_long_strike)                    
        Put_Spread.Open(stock_price, 
                    trade_date, 
                    fund_to_use/2, 
                    sigma, 
                    dividend)                            

        Call_Spread = Spread('Call', exp_date, call_short_strike, call_long_strike)        
        Call_Spread.Open(stock_price, 
                    trade_date, 
                    fund_to_use, 
                    sigma, 
                    dividend)               
              
        if Put_Spread.Contract == 0 or Call_Spread.Contract == 0:
            logger.debug('Short Iron Condor %s insuffient fund %.2f' % (trade_date.strftime("%m-%d-%y"), fund_to_use))            
            #print('Short Iron Condor %s insuffient fund %.2f' % (trade_date.strftime("%m-%d-%y"), fund_to_use))            
            return         
        
        contract = min(Put_Spread.Contract, Call_Spread.Contract)        
        Put_Spread.Contract = contract
        Call_Spread.Contract = contract
                
        if self.confirm_order(i, Put_Spread, trend, exp_date):        
            if self.confirm_order(i,Call_Spread, trend, exp_date) == False:
                logger.debug("Cannot establish call leg of short iron condor")                
                #print("Cannot establish call leg of short iron condor")                     
                self.Open_Positions.pop() 
        else:
            logger.debug("Cannot establish put leg of short iron condor")                
            #print("Cannot establish put leg of short iron condor")                 
            