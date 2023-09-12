UNPAIRED        	    = 'Unpaired'

LONG_CALL               = 'Long Call'
LONG_PUT                = 'Long Put'
COVERED_CALL            = 'Covered Call'
SHORT_PUT               = 'Short Put'   

CREDIT_CALL_SPREAD      = 'Credit Call Spread'
CREDIT_PUT_SPREAD       = 'Credit Put Spread'
DEBIT_CALL_SPREAD       = 'Debit Call Spread'
DEBIT_PUT_SPREAD        = 'Debit Put Spread'

CREDIT_IRON_CONDOR      = 'Credit Iron Condor'
DEBIT_IRON_CONDOR       = 'Debit Iron Condor' 

CREDIT_CALL_BUTTERFLY   = 'Credit Call Butterfly'
CREDIT_PUT_BUTTERFLY    = 'Credit Put Butterfly'
DEBIT_CALL_BUTTERFLY    = 'Debit Call Butterfly'
DEBIT_PUT_BUTTERFLY     = 'Debit Put Butterfly'
IRON_BUTTERFLY          = 'Iron Butterfly'
REVERSE_IRON_BUTTERFLY  = 'Reverse Iron Butterfly'

WEEKLY_STOCK_TRADE      = 'Weekly Stock Trade'

SINGLE_LIST =      [LONG_CALL, LONG_PUT, COVERED_CALL, SHORT_PUT]
SPREAD_LIST =      [CREDIT_PUT_SPREAD, DEBIT_PUT_SPREAD, CREDIT_CALL_SPREAD, DEBIT_PUT_SPREAD]
IRON_CONDOR_LIST = [CREDIT_IRON_CONDOR, DEBIT_IRON_CONDOR]         
BUTTERFLY_LIST =   [CREDIT_CALL_BUTTERFLY, CREDIT_PUT_BUTTERFLY, DEBIT_CALL_BUTTERFLY, DEBIT_PUT_BUTTERFLY, IRON_BUTTERFLY, REVERSE_IRON_BUTTERFLY]

ALL_STRATEGY = SINGLE_LIST + SPREAD_LIST  + IRON_CONDOR_LIST + BUTTERFLY_LIST

NEUTRAL_LIST =     [CREDIT_IRON_CONDOR, DEBIT_IRON_CONDOR, IRON_BUTTERFLY]
BULLISH_LIST =     [LONG_CALL, SHORT_PUT, CREDIT_PUT_SPREAD, DEBIT_CALL_SPREAD]
BEARISH_LIST =     [LONG_PUT, COVERED_CALL, DEBIT_PUT_SPREAD, CREDIT_CALL_SPREAD]      
BIGMOVE_LIST =     [REVERSE_IRON_BUTTERFLY] #long straddle 


PRICE_RANGE_BY_OPTION_STRADDLE  = 'by option straddle'
PRICE_RANGE_BY_RANDOM_WALK      = 'by random walk'
PRICE_RANGE_BY_LAST_NDAYS_RANGE = 'by last N days range'

'''
REVERSE IRON BUTTERFLY
A reverse iron butterfly is a multi-leg, risk-defined, neutral options strategy 
with limited profit potential. It is designed to take advantage of a rise in 
volatility and large price movement from the underlying asset 1. It involves 
buying a bull call debit spread and a bear put debit spread with the long options 
centered at the same strike price.

The best time to enter into a reverse iron butterfly is when you expect the 
underlying asset to make a large move in either direction before expiration 
and when implied volatility is expected to increase 1. This strategy profits 
the most when the underlying asset makes a large move and/or when implied 
volatility increases.
'''