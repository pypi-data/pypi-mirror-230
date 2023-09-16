from tradeBot.settings.tradeConfig import entryCrit
from tradeBot.settings.tradeConfig import exitCrit
from tradeBot.settings.tradeConfig import runtimeConfig
from tradeBot.settings.tradeConfig import marketCondition
from tradeBot.settings.tradeConfig import riskManager

from tradeBot.utils.optionTool import time_to_maturity_in_year

from datetime import time, date, datetime, timedelta

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bt_strategy')

class __State(object):
    def __init__(self, data_size):     
        self.Bottom = [np.nan] * data_size
        self.Top = [np.nan] * data_size
        
        self.Trend = ["no trend"] * data_size
        self.Slope = [np.nan] * data_size
     
        self.last_buttom = np.nan
        self.last_top = np.nan
        self.prev_turn = 0   
        

class _PerfCounter(object):
    def __init__(self):
        self.count = 0
        self.win_count = 0
        self.profit = 0
        self.win_profit = 0
        self.loss_profit = 0
        self.perf = 0        

class strategy(object):

    def __init__(self,
                 runtime_config = runtimeConfig(),
                 market_condition=marketCondition(),
                 risk_mgr = riskManager(),
                 entry_crit = entryCrit(),
                 exit_crit = exitCrit()):

        self.risk_mgr = risk_mgr
        self.entry_crit = entry_crit
        self.exit_crit = exit_crit
        self.runtime_config = runtime_config
        self.market_condition = market_condition
                
    def init_backtest(self, data):
        self.data = data
        self.fund_alloc = self.risk_mgr.init_fund_alloc
        self.perf_counter = _PerfCounter()         
        self.Open_Positions = []        
                          
    def pre_check_entry(self, i, x):
        sigma = self.data['rolling_sigma'][i]                            
        trade_date = self.data.index[i]               
        stock_price = self.data['Close'][i]                    
        
        if self.data.index[i].dayofweek != self.runtime_config.weekday:
            return  [None, None, None, None]  
        
        if self.fund_alloc <= 0:
            logger.debug("out of fund")
            return  [None, None, None, None]  

        if len(self.Open_Positions) >= self.risk_mgr.max_open_position:
            logger.debug('Max open position %.2f exceeded max_open_position %.2f' %
                        (len(self.Open_Positions), self.risk_mgr.max_open_position))
            return  [None, None, None, None]  

        days_to_expire = (4-self.runtime_config.weekday) + (7 * self.runtime_config.nweek)        
        if days_to_expire == 0: # if Friday and expire right away
            days_to_expire = 7                       
        exp_date = self.data.index[i] + timedelta(days=days_to_expire)          
        if exp_date not in self.data.index:
            logger.debug('Market not open or in the future for Exp Date:'+str(exp_date))
            return  [None, None, None, None]  
        
        return [exp_date, sigma, trade_date, stock_price] 
                 
        
    def confirm_order(self, i, Spread, trend, exp_date): # for spread positions
                                   
        stock_price = self.data['Close'][i]
        trade_date = self.data.index[i]
        
        if Spread.Credit_Spread == True:
            pnl = Spread.Open_Price / (Spread.Spread - Spread.Open_Price)                               
        else: # debit spread
            pnl =(Spread.Spread - Spread.Open_Price)/Spread.Open_Price
        
        if Spread.Credit_Spread and pnl <  self.entry_crit.min_pnl:
            logger.debug('%s pnl %.2f less than min_pnl %.2f' % (trade_date.strftime("%m-%d-%y"), pnl, self.entry_crit.min_pnl))                
            #print('%s pnl %.2f less than min_pnl %.2f' % (trade_date.strftime("%m-%d-%y"), pnl, self.entry_crit.min_pnl))                            
            return False                          

        logger.debug('%s fund before open new position %.2f' % 
                  (trade_date.strftime("%m-%d-%y"), self.fund_alloc)) 
            
        if Spread.Credit_Spread == True:
            self.fund_alloc -= Spread.Margin_Per_Contract * Spread.Contract * 100                                 
        else: # debit spread
            self.fund_alloc -= Spread.Open_Price * Spread.Contract * 100                                 
        
        self.Open_Positions.append(Spread)         
        
        logger.debug('%s OPEN %s SPREAD exp %s %.2f contracts [%s slope %.2f]  credit %.2f margin %.2f s strike %.2f l strike %.2f stock %.2f U %.2f M %.2f L %.2f %s max_fund %.2f' % 
                  (trade_date.strftime("%m-%d-%y"),
                   Spread.Type,
                   exp_date.strftime("%m-%d-%y"),
                   Spread.Contract,                
                   trend.trend,
                   trend.slope,                   
                   Spread.Open_Price, 
                   Spread.Margin_Per_Contract,                                    
                   Spread.Short_Strike,  
                   Spread.Long_Strike,                     
                   stock_price,                                   
                   self.data['BBU_20_2.0'][i], 
                   self.data['BBM_20_2.0'][i],
                   self.data['BBL_20_2.0'][i],
                   exp_date.strftime("%m-%d-%y"),
                   self.fund_alloc))          
                 
        return True
    
    def check_exit(self, i, dividend): # for spread position
        if len(self.Open_Positions) > 0:        
            sigma = self.data['rolling_sigma'][i]         
            stock_price = self.data['Close'][i]   
            trade_date = self.data.index[i]

            for Spread in self.Open_Positions:
                if time_to_maturity_in_year(trade_date, Spread.Exp_Date) <= 0:           
                    exp_date_price = self.data['Close'][Spread.Exp_Date]
                    exp_date_sigma = self.data['rolling_sigma'][Spread.Exp_Date]
                    Spread.Close(exp_date_price, Spread.Exp_Date, exp_date_sigma)    
                    logger.debug('%s Expired stock price %.2f' % (trade_date.strftime("%m-%d-%y"), stock_price))                       
                else:                                
                    spread_current_value = Spread.current_price_per_contract(stock_price, self.data.index[i], sigma, dividend)                                                                                           
                    if Spread.Credit_Spread:
                        gain = Spread.Open_Price - spread_current_value
                    else:
                        gain = spread_current_value - Spread.Open_Price
                        
                    gain = 100 * (gain / Spread.Open_Price)   
                                        
                    logger.debug('%s GAIN %.2f current value %.2f credit %.2f stock %.2f' % 
                              (trade_date.strftime("%m-%d-%y"), gain, spread_current_value, Spread.Open_Price,stock_price))

                    if (gain > 0 and gain > self.exit_crit.stop_gain) or (gain < 0 and -1 * gain > self.exit_crit.stop_loss):
                        Spread.Close(stock_price, trade_date, sigma, dividend)                
                        
                        logger.debug('%s STOP stock %.2f put value %.2f gain %.2f stop_gain %.2f stop_loss %.2f' % 
                                  (trade_date.strftime("%m-%d-%y"),
                                   stock_price,
                                   spread_current_value,                                
                                   gain, 
                                   self.exit_crit.stop_gain, 
                                   self.exit_crit.stop_loss))    
  
                if Spread.Status == 'Closed':
                    p = self.post_position_close(trade_date, Spread)
                    self.Open_Positions.remove(Spread)             
                    if p > 0:
                        win_loss = 'WIN'
                    else:
                        win_loss = 'LOSS'

                    logger.debug( '%s %s stock %.2f Profit %.2f [%d/%d] Fund %.2f Total Profit %.2f win %.2f loss %.2f' %  
                              (trade_date.strftime("%m-%d-%y"),
                               win_loss,
                               stock_price,                            
                               Spread.Profit_Per_Contract, 
                               self.perf_counter.win_count, 
                               self.perf_counter.count,
                               self.fund_alloc,
                               self.perf_counter.profit,
                               self.perf_counter.win_profit,
                               self.perf_counter.loss_profit))       
    
    
    def post_position_close(self, trade_date, Spread):  # for spread positions          

        logger.debug('%s fund before close position %.2f profit %.2f credit %.2f margin %.2f contract %.2f' % (
                trade_date.strftime("%m-%d-%y"), self.fund_alloc, Spread.Profit_Per_Contract, Spread.Open_Price, Spread.Margin_Per_Contract, Spread.Contract)  )
            
        if Spread.Credit_Spread:
            self.fund_alloc += 100 * ((Spread.Margin_Per_Contract + Spread.Profit_Per_Contract) * Spread.Contract)                                   
        else:
            self.fund_alloc += 100 * (Spread.Profit_Per_Contract + Spread.Open_Price) * Spread.Contract                         

        logger.debug('%s fund after close position %.2f' % (trade_date.strftime("%m-%d-%y"), self.fund_alloc))

        p = Spread.Profit_Per_Contract * Spread.Contract * 100
        
        self.perf_counter.count += 1 
        self.perf_counter.profit += p      
        #print('fund %.2f margin %.2f' % (self.risk_mgr.fund_alloc, Spread.Margin_Per_Contract))
        if p > 0:
            self.perf_counter.win_count += 1                     
            self.perf_counter.win_profit += p
        else:
            self.perf_counter.loss_profit += p 
        
        return p
    
    def get_name(self):
        return self.__class__.__name__
    
    def get_short_name(self):
        return self.__class__.__name__    
    
    def get_gain(self):
        return 100 * self.perf_counter.profit/self.risk_mgr.init_fund_alloc
    
    def report(self):
        print('%s : win/total count %d/%d gain %.2f%%' % 
            (self.get_name(), self.perf_counter.win_count, self.perf_counter.count, 100 * (self.perf_counter.profit/self.risk_mgr.init_fund_alloc)))
    