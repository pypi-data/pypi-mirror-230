from tradeBot.backtest.option import strategy
from tradeBot.settings.tradeConfig import entryCrit
from tradeBot.settings.tradeConfig import exitCrit
from tradeBot.settings.tradeConfig import runtimeConfig
from tradeBot.settings.tradeConfig import marketCondition
from tradeBot.settings.tradeConfig import riskManager

from tradeBot.utils.optionTool import BSCallStrikeFromDelta
from tradeBot.utils.optionTool import Call
from tradeBot.utils.optionTool import Put
from tradeBot.utils.optionTool import time_to_maturity_in_year

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('bt_single_option')

class bt_single_option(strategy.strategy):
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
        if self.Credit == False:
            if self.Type == 'Call':
                return 'Long Call'
            else:
                return 'Long Put'
        else:
            if self.Type == 'Call':
                return 'Covered Call'
            else:
                return 'Short Put'           
    
    def check_entry(self, i, dividend, trend):
                
        exp_date, sigma, trade_date, stock_price =  self.pre_check_entry(i, trend)      
        if exp_date == None:
            return
        
        fund_to_use = self.fund_alloc * self.risk_mgr.pos_max_alloc_pert
        
        if self.Type == 'Call' and self.Credit==False and trend.trend == 'decreasing':
            return
        
        if self.Type == 'Call' and self.Credit and trend.trend == 'increasing':
            return        
        
        if self.Type == 'Put' and self.Credit==False and trend.trend == 'increasing':
            return
        
        if self.Type == 'Put' and self.Credit == False and trend.trend == 'decreasing':
            return
            
        if self.Type == 'Call' and self.Credit: # covered call                         
            strike = BSCallStrikeFromDelta(stock_price, trade_date, exp_date, sigma=sigma, delta=self.entry_crit.max_delta_for_short)              
        else:
            strike = stock_price     
              
        if self.Type == 'Call':
            pos = Call(strike, exp_date)            
        else:
            pos = Put(strike, exp_date)
        
        if self.Credit:
            pos.sell_to_open(stock_price, trade_date, fund_to_use, sigma, dividend) 
        else:
            pos.buy_to_open(stock_price, trade_date, fund_to_use, sigma, dividend)             
            
        if pos.Contract == 0:
            logger.debug('%s %s insuffient fund %.2f' % (pos.Type, trade_date.strftime("%m-%d-%y"), fund_to_use))            
            return 
                
        # confirm order           
        if self.Credit == False:
            pos.Contract = fund_to_use / (pos.Open_Price * 100)
            self.fund_alloc -= pos.Open_Price * pos.Contract * 100                                 
        else:
            if self.Type == 'Call': # covered call
                pos.Contract = self.entry_crit.covered_call_contract
                pos.Margin_Required_Per_Contract = 0            
                self.fund_alloc += pos.Open_Price * pos.Contract * 100                   
            else:
                pos.Contract = fund_to_use / (pos.Margin_Required_Per_Contract * 100)
                self.fund_alloc -= (pos.Margin_Required_Per_Contract - pos.Open_Price) * pos.Contract * 100   
                            
        self.Open_Positions.append(pos)         
        
        if self.Credit:
            ttype = 'Sell to Open'
        else:
            ttype = 'Buy to Open'

        logger.debug('%s [%s slope %.2f] %s %.2f contracts: credit %.2f margin %.2f strike %.2f stock %.2f U %.2f M %.2f L %.2f %s max_fund %.2f' % 
              (trade_date.strftime("%m-%d-%y"),
               trend.trend,
               trend.slope,
               ttype,
               pos.Contract,                                   
               pos.Open_Price,   
               pos.Margin_Required_Per_Contract,
               pos.Strike,                    
               stock_price,                                   
               self.data['BBU_20_2.0'][i], 
               self.data['BBM_20_2.0'][i],
               self.data['BBL_20_2.0'][i],
               exp_date.strftime("%m-%d-%y"),
               self.fund_alloc))          

    def check_exit(self, i, dividend):
        if len(self.Open_Positions) > 0:        
            sigma = self.data['rolling_sigma'][i]         
            stock_price = self.data['Close'][i]   
            trade_date = self.data.index[i]

            for pos in self.Open_Positions:

                if time_to_maturity_in_year(trade_date, pos.Exp_Date) <= 0:           
                    exp_date_price = self.data['Close'][pos.Exp_Date]
                    exp_date_sigma = self.data['rolling_sigma'][pos.Exp_Date]
                    
                    if self.Credit:
                        pos.buy_to_close(exp_date_price, pos.Exp_Date, sigma, dividend)
                    else:
                        pos.sell_to_close(exp_date_price, pos.Exp_Date, sigma, dividend)                               
                        
                    logger.debug('%s Expired' % trade_date.strftime("%m-%d-%y"))                       
                    expired = True
                else:                                
                    pos_current_value = pos.current_price_per_contract(stock_price, self.data.index[i], sigma, dividend)                                                                                           

                    if self.Credit:
                        gain = pos.Open_Price - pos_current_value
                    else:
                        gain = pos_current_value - pos.Open_Price                        
                        
                    gain = 100 * (gain / pos.Open_Price)                           
                                    
                    logger.debug('%s GAIN %.2f current value %.2f credit %.2f stock %.2f' % 
                              (trade_date.strftime("%m-%d-%y"), gain, pos_current_value, pos.Open_Price,stock_price))

                    if (gain > 0 and gain > self.exit_crit.stop_gain) or (gain < 0 and -1 * gain > self.exit_crit.stop_loss):
                        if self.Credit:
                            pos.buy_to_close(stock_price, trade_date, sigma, dividend)  
                        else:
                            pos.sell_to_close(stock_price, trade_date, sigma, dividend)      
                            
                        logger.debug('%s STOP stock %.2f put value %.2f gain %.2f stop_gain %.2f stop_loss %.2f' % 
                                  (trade_date.strftime("%m-%d-%y"),
                                   stock_price,
                                   pos_current_value,                                
                                   gain, 
                                   self.exit_crit.stop_gain, 
                                   self.exit_crit.stop_loss))    
  
                if pos.Status == 'Closed':
                    if self.Credit:
                        if pos.Type == 'Call': # covered call open price value already added to fund_alloc
                            self.fund_alloc -= 100 * (pos.Open_Price - pos.Profit_Per_Contract) * pos.Contract  
                        else:
                            self.fund_alloc += 100 * (pos.Margin_Required_Per_Contract+(pos.Open_Price - pos.Profit_Per_Contract)) * pos.Contract                              
                    else:
                        self.fund_alloc += 100 * (pos.Profit_Per_Contract+pos.Open_Price) * pos.Contract                         
                        
                    p = pos.Profit_Per_Contract * pos.Contract * 100
                    self.perf_counter.count += 1 
                    self.perf_counter.profit += p      
                    if p > 0:
                        self.perf_counter.win_count += 1                     
                        self.perf_counter.win_profit += p
                    else:
                        self.perf_counter.loss_profit += p 
         
                    self.Open_Positions.remove(pos)             
                    if p > 0:
                        win_loss = 'WIN'
                    else:
                        win_loss = 'LOSS'

                    logger.debug('%s %s stock %.2f Profit/Contract %.2f [%d/%d] Fund %.2f Total Profit %.2f win %.2f loss %.2f' %                               
                               (trade_date.strftime("%m-%d-%y"),
                               win_loss,
                               stock_price,                            
                               pos.Profit_Per_Contract, 
                               self.perf_counter.win_count, 
                               self.perf_counter.count,
                               self.fund_alloc,
                               self.perf_counter.profit,
                               self.perf_counter.win_profit,
                               self.perf_counter.loss_profit))              