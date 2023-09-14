
# site.db
site_profile = "site_name TEXT NOT NULL PRIMARY KEY, region TEXT, default_strategy_list TEXT, default_watchlist TEXT, default_notification_token TEXT"

site_monitor_db = "symbol TEXT NOT NULL PRIMARY KEY, last_price REAL, support REAL, resistence REAL,\
    rating REAL, trend TEXT, slope REAL, bb_pos TEXT, bb_link TEXT, rsi TEXT, rsi_link TEXT,\
    macd TEXT, macd_link TEXT, mfi TEXT, mfi_link TEXT, earning TEXT, day_range_pos REAL,\
    fifty_weeks_range_pos REAL, volume_range_pos REAL, forward_PE REAL, HV REAL,\
    IV1 REAL, delta1 REAL,IV2 REAL, delta2 REAL,IV3 REAL, delta3 REAL,IV4 REAL, delta4 REAL,\
    quote_time TEXT"

user_list = "user_name TEXT NOT NULL PRIMARY KEY, db_path TEXT NOT NULL"

# user.db
user_profile = "name TEXT NOT NULL PRIMARY KEY, email TEXT, default_strategy_list TEXT, default_watchlist TEXT, notification_token TEXT,  billing TEXT"

#watchlist   =  "name TEXT NOT NULL PRIMARY KEY, symbol_list TEXT"

account_list = "account_name TEXT NOT NULL PRIMARY KEY, db_path TEXT NOT NULL"

'''
# account.db
account_profile_schema = "user_name TEXT, account_name TEXT NOT NULL PRIMARY KEY,equaty_percentage REAL,\
        available_to_tread REAL,available_to_trade_wo_margin REAL,non_margin_buy_power REAL,\
        margin_buy_power REAL,available_to_withdraw REAL,cash_only REAL,cash_and_margin REAL,\
        house_surplus REAL,sma REAL,exchange_surplue REAL,cash_core REAL,cash_credit_debit REAL,\
        margin_credit_debit REA,market_value_securities REAL,held_in_cash REAL, held_in_margin REAL,\
        cash_buy_power REAL,settled_cash REAL,initial_balance REAL,risk_mgr TEXT, entry_crit TEXT,\
        market_condition TEXT, runtime_config TEXT,default_strategy_list TEXT, default_watchlist TEXT, default_predictor TEXT,\
        FOREIGN KEY(user_name) REFERENCES user(name)"    


positionSummary = "symbol TEXT,strategy TEXT,status TEXT,\
        spread REAL, open_price REAL,breakeven_l REAL, breakeven_h REAL,\
        max_prifit REAL, max_loss REAL,pnl REAL,win_prob REAL,\
        trade_date REAL,earning_date TRXT,trade_stock_price REAL,\
        margin REAL,quantity REAL,option_legs TEXT,\
        last_quote_date REAL, last_stock_price REAL,exp_stock_price REAL,\
        last_price REAL,exp_price REAL,pl REAL,gain REAL,\
        stop_price REAL,stop_date TEXT,stop_reason TEXT,\
        order_id TEXT,uuid TEXT,\
        primary key(uuid)"

position = "symbol TEXT, otype TEXT, open_action TEXT, quantity REAL, strike REAL, exp_date TEXT,\
    last_price REAL, current_value REAL, total_gain_loss REAL, total_gain_loss_percent REAL,\
    average_cost_basis REAL, init_delta REAL, init_IV REAL, init_volume REAL, init_open_interest,\
    last_delta REAL, last_IV REAL, last_volume, REAL last_open_interest,status TEXT, uuid TEXT,\
    FOREIGN KEY(uuid) REFERENCES strategy_position(uuid)"

transactions = "trx_time TEXT,symbol TEXT,otype TEXT,buy_sell TEXT,open_close TEXT,\
    strike REAL,exp_date TEXT,quantity REAL,price REAL,commission REAL,fee REAL,amount REAL"
'''