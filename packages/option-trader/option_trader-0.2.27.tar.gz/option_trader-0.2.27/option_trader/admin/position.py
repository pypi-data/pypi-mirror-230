
schema = "symbol TEXT, otype TEXT, open_action TEXT, quantity REAL, strike REAL, exp_date TEXT,\
         open_price REAL, last_price REAL, current_value REAL, total_gain_loss REAL,\
         trade_date TEXT, last_quote_date TEXT,total_gain_loss_percent REAL,\
         average_cost_basis REAL, init_delta REAL, init_IV REAL,\
         init_volume REAL, init_open_interest INTEGER, last_delta REAL, last_IV REAL, last_volume REAL,\
         last_open_interest INTEGER,status TEXT, leg_id INTEGER, uuid TEXT,\
         FOREIGN KEY(uuid) REFERENCES position_summary(uuid)"

SYMBOL                   = 'symbol'
OTYPE                    = 'otype'     
QUANTITY                 = 'quantity' 
STRIKE                   = 'strike'       
EXP_DATE                 = 'exp_date' 
OPEN_PRICE               = 'open_price'
OPEN_ACTION              = 'open_action'
TRADE_DATE               = 'trade_date'
LAST_QUOTE_DATE          = 'last_quote_date'
LAST_PRICE               = 'last_price'            
CURRENT_VALUE            = 'current_value'         
TOTAL_GAIN_LOSS          = 'total_gain_loss'
TOTAL_GAIN_LOSS_PERCENT  = 'total_gain_loss_percent'        
TOTAL_COST_BASIS         = 'total_cost_basis'
AVERAGE_COST_BASIS       = 'average_cost_basis'
INIT_DELTA               = 'init_delta'    
LAST_DELTA               = 'last_delta'        
INIT_IV                  = 'init_IV'
LAST_IV                  = 'last_IV'
INIT_VOLUME              = 'init_volume'
LAST_VOLUME              = 'last_volume'
INIT_OPEN_INTEREST       = 'init_open_interest'
LAST_OPEN_INTEREST       = 'last_open_interest'
STATUS                   = 'status'    
UUID                     = 'uuid' 
LEG_ID                   = 'leg_id'
OPEN_ACTION              = 'open_action' # SELL or BUY
SCALE                    = 'scale'

class position():

    def __init__(self):
        return