from pathlib import Path

from option_trader.consts import strategy

OPTION_TRADER = 'option_trader'

def OPTION_TRADER_BASE_DIR():
    p = str(Path().resolve())
    l = p.find(OPTION_TRADER)   
    if l >= 0:
        return p[: l + len(OPTION_TRADER)]       
    else:
        return None        

import os

SERVICE_ROOT_DIR    = OPTION_TRADER_BASE_DIR()
SITE_ROOT_DIR       = os.path.join(SERVICE_ROOT_DIR,'sites')
DATA_ROOT_DIR       = os.path.join(SERVICE_ROOT_DIR, 'data')
CHART_ROOT_DIR      = os.path.join(DATA_ROOT_DIR, 'charts')
LOG_ROOT_DIR        = os.path.join(DATA_ROOT_DIR,'logs')
SITE_USER_DIR       = 'users'
#TRADINGBOT_HOME_DIR = SITE_ROOT_DIR+'/src'

TREND_WINDOW_SIZE = 7
USE_PANDA = False
TRADE_IB = False

LINE_CHANNEL_SECRET = '628e7b113c8927a8a81e6e5f34412ffe'
LINE_USER_ID = '628e7b113c8927a8a81e6e5f34412ffe'
LINE_BOT_BASIC_ID = '@713hvlic'
LINE_CHANNEL_ACCESS_TOKEN = 'eNyfeZLsU7MbVSU8oWu+iryZ6yzVuO575vB71iNtjBbbNznkoPfsTbxhz+hbHX1m745hV/Zm90r4/fsUFTKeB9I5axHBQC4jRPMqAxniBO2wkVzdNs9X28czaoKixH1lxaefvcLEtFkZMqy2qNs8vwdB04t89/1O/w1cDnyilFU='
LINE_NOTIFICATION_TOKEN = '2IXx92MpbbYfkdkpXAp5dHtopLWlxwqRM68SMuJClpD'
MY_GMAIL_PASSWORD = "sdhbjsuhudmvuugp"

DEFAULT_SITE_STRATEGY_LIST = strategy.ALL_STRATEGY
DEFAULT_SITE_WATCHLIST = ['MSFT', 'AAPL', 'AMZN', 'BLDR', 'GOOGL', 'NFLX', 'META', 'SPY', 'QQQ']
DEFAULT_SITE_NOTIFICATION_TOKEN = LINE_NOTIFICATION_TOKEN

TIMEZONE   ='US/Eastern'
DATABASES  ='sqlite3'
DEFAULT_ACCOUNT_INITIAL_BALANCE = 100000
TARGET_PROB=50
PRICE_RANGE_PREDICT_ALGO = strategy.PRICE_RANGE_BY_LAST_NDAYS_RANGE
PREDICT_WINDOW = 20

LOGGER_NAME =  '__name__' #'debug_level_log'

GOOGLE_OUTH_CLIENT_ID = "844605684221-8o8t98bje2mbkr8n6uuqc9k0utgfr7uv.apps.googleusercontent.com"

GOOGLE_OUTH_SECRETE = "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"

if __name__ == '__main__':

    print(DATA_ROOT_DIR)

    #import re
    #p = str(Path().resolve())
    #print(p)
    #match = re.search(r"[^a-zA-Z]("+OPTION_TRADER+")[^a-zA-Z]", p)        
    #if match != None:
    #    l = match.start(1) + len(OPTION_TRADER)
    #    print(p[:l])


    #print(DATA_ROOT_DIR)