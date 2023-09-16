
from scipy.stats import norm
import numpy as np
import pandas as pd
import logging


def BSPutStrikeFromDelta(S, trade_date, exp_date, sigma, delta, r=0.03):
    T = time_to_maturity_in_year(trade_date, exp_date)
    N = norm.cdf        
    return S * np.exp(-N(delta * np.exp((r)*T) ) * sigma * np.sqrt(T) + ((sigma**2)/2) * T)

def BSCallStrikeFromDelta(S, trade_date, exp_date, sigma, delta, r=0.03):
    T = time_to_maturity_in_year(trade_date, exp_date)
    N = norm.cdf        
    return S * np.exp(N(delta* np.exp((r)*T) ) * sigma * np.sqrt(T) + ((sigma**2)/2) * T)

    
#https://www.codearmo.com/python-tutorial/options-trading-black-scholes-model
#http://www.smileofthales.com/computation/option-greeks-python-math-proof/

#S = 100 #stock price S_{0}
#K = 110 # strike
#T = 1/2 # time to maturity in year
#r = 0.05 # risk free risk in annual %
#q = 0.02 # annual dividend rate
#sigma = 0.25 # annual volatility in %
#   call_delta =math.exp(-q*t)*norm.cdf(d1)
#   put_delta =math.exp(-q*t)*(norm.cdf(d1)-1)
         
def d1(S, K, T, r, sigma):

    logger = logging.getLogger(__name__)    
    if T <= 0:
        logger.error('Zero T')      
    return (np.log(S/K) + (r + sigma**2/2)*T) / sigma*np.sqrt(T)
    
def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma* np.sqrt(T)

def delta_call(S, K, T, sigma=0.25, r=0.05):
    N = norm.cdf
    return N(d1(S, K, T, r, sigma))

def theta_call(S, K, T,sigma=0.25, r=0.05):
    return (-S * norm.pdf(d1(S, K, T, r, sigma)) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2(S, K, T, r, sigma))) / 365

def delta_put(S, K, T, sigma=0.25, r=0.05):
    N = norm.cdf        
    return - N(-d1(S, K, T, r, sigma))

def theta_put(S, K, T, sigma=0.25, r=0.05): 
    return (-S * norm.pdf(d1(S, K, T, r, sigma)) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2(S, K, T, r, sigma))) / 365

def gamma(S,T, K, sigma=0.25, r=0.05):
    return norm.pdf(d1(S, K, T, r, sigma)) / (S * sigma * np.sqrt(T))

def vega(S,T, K,sigma=0.25, r=0.05):
    return S * norm.pdf(d1(S, K, T, r, sigma)) * np.sqrt(T) / 100

def delta_fdm_call(S, K, T, r, sigma, ds = 1e-5, method='central'):
    method = method.lower() 
    if method =='central':
        return (BS_CALL(S+ds, K, T, r, sigma) -BS_CALL(S-ds, K, T, r, sigma))/(2*ds)
    elif method == 'forward':
        return (BS_CALL(S+ds, K, T, r, sigma) - BS_CALL(S, K, T, r, sigma))/ds
    elif method == 'backward':
        return (BS_CALL(S, K, T, r, sigma) - BS_CALL(S-ds, K, T, r, sigma))/ds

def delta_fdm_put(S, K, T, r, sigma, ds = 1e-5, method='central'):
    method = method.lower() 
    if method =='central':
        return (BS_PUT(S+ds, K, T, r, sigma) -BS_PUT(S-ds, K, T, r, sigma))/\
                        (2*ds)
    elif method == 'forward':
        return (BS_PUT(S+ds, K, T, r, sigma) - BS_PUT(S, K, T, r, sigma))/ds
    elif method == 'backward':
        return (BS_PUT(S, K, T, r, sigma) - BS_PUT(S-ds, K, T, r, sigma))/ds

def BS_CALL(S, K, T, sigma, q=0, r=0.03):
    logger = logging.getLogger(__name__)    
    try:
        N = norm.cdf    
        d1 = (np.log(S/K) + (r - q + sigma**2/2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma* np.sqrt(T)
        return S*np.exp(-q*T) * N(d1) - K * np.exp(-r*T)* N(d2)
    except Exception as e:
        logger.error('BA_CALL exception'+str(e))   
        return np.nan                   

def BS_PUT(S, K, T, sigma, q=0, r=0.03):
    logger = logging.getLogger(__name__)        
    try:
        N = norm.cdf        
        d1 = (np.log(S/K) + (r - q + sigma**2/2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma* np.sqrt(T)
        return K*np.exp(-r*T)*N(-d2) - S*np.exp(-q*T)*N(-d1)
    except Exception as e:
        logger.error('BS_PUT exception'+str(e))            
        return np.nan

#T = 1/2 # time to maturity in year
def time_to_maturity_in_year(start_date, exp_date):   
    logger = logging.getLogger(__name__)        
    days_to_expire = (pd.Timestamp(exp_date).date()-start_date).days
    if days_to_expire < 0:
        logger.error('start date %s same or beyond exp date %s' %(str(start_date), str(exp_date)))
    return days_to_expire / 365