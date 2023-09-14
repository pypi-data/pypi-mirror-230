import pandas as pd
import numpy  as np
import math

from  option_trader.settings import ib_config as ic
from  option_trader.admin import quote

from ib_insync import *

import logging

from option_trader.settings import app_settings    


class IBClient:    

    connection = None     
    bool = API_opened = True

    @staticmethod
    def get_client():

        logger = logging.getLogger(__name__)  

        if IBClient.API_opened == False:
            return None

        try:
            get_ipython    
            util.startLoop()  # uncomment this line when in a notebook
        except:
            pass        
      
        if IBClient.connection == None:
            try:      
                ib = IB()
                ib.connect('127.0.0.1', ic.IBConfig.port, clientId=ic.IBConfig.clientId)            
                IBClient.connection = ib
                # delayed quote
                ib.reqMarketDataType(ic.IBConfig.marketDataType)            
                return ib
            except Exception as e:
                logger.exception(e)
                logger.info("IB not connected get data from Yahoo instead")                    
                IBClient.API_opened = False
                return None                  
        else:
            return IBClient.connection
        
    @staticmethod
    def disconnect():
        if IBClient.connection != None:
            IBClient.connection.client.disconnect()
            IBClient.connection = None     

def IB_get_price_history(symbol, period="1 Y", interval="1 day", start=None, end=None):    


    
    ib = IBClient.get_client()
    
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"

    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr=period,
        barSizeSetting=interval, whatToShow='TRADES', useRTH=True)

    df =  util.df(bars)
    #df.rename(columns = {'date':'Date', 'open':'Open', 'high':'High', 'low':'Low',
    #                     'close':'Close', 'volume':'Volume', 'average':'Average'}, inplace = True)
    
    IBClient.disconnect()
    
    return df.set_index('Date')

option_chain_rec = { quote.EXP_DATE:[''],quote.STRIKE:[np.nan],
                quote.LAST_PRICE:[np.nan],quote.BID:[np.nan], quote.ASK:[np.nan],
                quote.BID_SIZE:[np.nan],quote.ASK_SIZE:[np.nan], quote.VOLUME:[np.nan], quote.OPEN_INTEREST:[np.nan],
                quote.OPEN:[np.nan], quote.HIGH:[np.nan], quote.LOW:[np.nan], quote.CLOSE:[np.nan],
                quote.IMPLIED_VOLATILITY:[np.nan], quote.DELTA:[np.nan], quote.GAMMA:[np.nan],
                quote.VEGA:[np.nan], quote.THETA:[np.nan]}

from option_trader.consts import asset as at

def IB_get_option_leg_details(symbol, exp_date, strike, otype):
    
    logger = logging.getLogger(__name__)

    ib = IBClient.get_client()
    if ib.isConnected() == False:
        logger.error('IB disconnected')

    if otype == at.CALL:
        otype = 'C'

    if otype == at.PUT:
        otype = 'P'

    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'OPT'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.lastTradeDateOrContractMonth = exp_date.strftime('%Y%m%d') #'20230512'
    contract.strike = strike
    contract.right = otype
    contract.multiplier = '100'
    ib.qualifyContracts(contract) 
    x = ib.reqMktData(contract, '', False, False, [])
    ib.sleep(5)

    #IBClient.disconnect()    

    if math.isnan(x.bid):
        logger.error("Failed to get option quote")
        return None
    
    if x.bid == -1:
        logger.error("Cannot get option quote outside market hours")
        return None    

    ne = pd.DataFrame.from_records(option_chain_rec)
    ne.exp_date = exp_date
    ne.strike = strike    
    ne.bid =  x.bid
    ne.bidSize = x.bidSize
    ne.ask = x.ask
    ne.askSize = x.askSize
    ne.lastPrice = x.last
    ne.open = x.open
    ne.high = x.high
    ne.low = x.low
    ne.close = x.close
    ne.openInterest = ne.bidSize
    if x.bidGreeks != None:
        ne.impliedVolatility = x.modelGreeks.impliedVol
        ne.delta = x.modelGreeks.delta
        ne.gamma = x.modelGreeks.gamma
        ne.vega  = x.modelGreeks.vega
        ne.theta = x.modelGreeks.theta
        ne.volume = x.volume
        
    return ne.to_dict('records')[0]

def IB_get_option_chain(symbol, exp_date, stock_price, max_strike_pert=0.05):
        
    logger = logging.getLogger(__name__)  
    try:
        get_ipython    
        util.startLoop()  # uncomment this line when in a notebook
    except:
        pass  

    ib = IBClient.get_client()
    if ib.isConnected() == False:
        logger.error('IB disconnected')

    x = ib.reqMatchingSymbols(symbol)
    conId = x[0].contract.conId

    x = ib.reqSecDefOptParams(symbol, "", "STK", conId)
   
    strikes = list(filter(lambda x: x >= stock_price * (1-max_strike_pert) and x <= stock_price * (1+max_strike_pert), x[0].strikes))   
    
    ib.reqMarketDataType(3)
        
    call_chain = put_chain = pd.DataFrame()

    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'OPT'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.lastTradeDateOrContractMonth = exp_date.strftime('%Y%m%d') 

    contract.multiplier = '100'
    
    for strike in strikes:                    
        contract.strike = strike

        contract.right = 'C'   
        ib.qualifyContracts(contract) 
        x = ib.reqMktData(contract, '', False, False, [])
        ib.sleep(5) 

        if math.isnan(x.bid) == False:           
            ne = pd.DataFrame.from_records(option_chain_rec)
            ne.exp_date = exp_date
            ne.strike = strike    
            ne.bid =  x.bid
            ne.bidSize = x.bidSize
            ne.ask = x.ask
            ne.askSize = x.askSize
            ne.lastPrice = x.last
            ne.open = x.open
            ne.high = x.high
            ne.low = x.low
            ne.close = x.close
            ne.openInterest = ne.bidSize

            if x.bidGreeks != None:
                ne.impliedVolatility = (x.bidGreeks.impliedVol + x.askGreeks.impliedVol) / 2
                ne.delta = (x.bidGreeks.delta + x.askGreeks.delta) / 2
                ne.gamma = (x.bidGreeks.gamma + x.askGreeks.gamma) / 2
                ne.vega =  (x.bidGreeks.vega + x.askGreeks.vega) / 2
                ne.theta = (x.bidGreeks.theta  + x.askGreeks.theta ) / 2
                ne.volume = x.volume

            call_chain = pd.concat([call_chain, ne])  

        contract.right = 'P'
        ib.qualifyContracts(contract) 
        x = ib.reqMktData(contract, '', False, False, [])
        ib.sleep(5)                 
       
        if math.isnan(x.bid) == False:           
            ne = pd.DataFrame.from_records(option_chain_rec)
            ne.exp_date = exp_date
            ne.strike = strike    
            ne.bid =  x.bid
            ne.bidSize = x.bidSize
            ne.ask = x.ask
            ne.askSize = x.askSize
            ne.lastPrice = x.last
            ne.open = x.open
            ne.high = x.high
            ne.low = x.low
            ne.close = x.close
            ne.openInterest = ne.bidSize
                                
            if x.bidGreeks != None:
                ne.impliedVolatility = (x.bidGreeks.impliedVol + x.askGreeks.impliedVol) / 2
                ne.delta = (x.bidGreeks.delta + x.askGreeks.delta) / 2
                ne.gamma = (x.bidGreeks.gamma + x.askGreeks.gamma) / 2
                ne.vega =  (x.bidGreeks.vega + x.askGreeks.vega) / 2
                ne.theta = (x.bidGreeks.theta  + x.askGreeks.theta ) / 2
                ne.volume = x.volume
                
            put_chain = pd.concat([put_chain, ne])              
                        
    #ib.disconnect()
    
    return call_chain, put_chain

 