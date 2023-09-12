def option_strategy_backtest( symbol, 
                             strategy_list, 
                             period="1y", 
                             interval="1d", 
                             start=None, 
                             end=None): 

    BBandStrategy = ta.Strategy(
        name="Momo and Volatility",
        description="BBANDS",
        ta=[
            {"kind": "bbands", "length": 20},      
        ]
    )   

    vix = get_price_history('^VIX', period, interval, start, end) 
    data = get_price_history(symbol, period, interval, start, end) 
    data.ta.cores = 2 
    data.ta.strategy(BBandStrategy)
    data.dropna(subset=["BBM_20_2.0"])
    data['change'] = data['Close'].pct_change()
    data['rolling_sigma'] = data['change'].rolling(20).std() * np.sqrt(255)    
    
    for strategy in strategy_list:
        strategy.init_backtest(data)

    dividend = get_latest_dividend(symbol)
    
    s = strategy.runtime_config.trend_window_size # sample size for Mann-Kendall Trend Test
    gfg_data = [0] * s 
        
    start = None
    for i in range(len(data)):
        # skip inital nan values
        if i <  s or pd.isna(data['BBM_20_2.0'][i-s+1] or pd.isna(data['rolling_sigma'][i])):               
            continue    

        if start == None:
            start = i
            
        for j in range(s):        
            gfg_data[j] = data['BBM_20_2.0'][i-s+1+j]   
           
        x = mk.original_test(gfg_data)
        
        for strategy in strategy_list:
            strategy.market_condition.current_vix = '%.2f' % vix['Close'][-1]
            strategy.check_exit(i, dividend)                                                     
            strategy.check_entry(i, dividend, x)                           
                     
    bench = 100 * ((data['Close'][-1] - data['Close'][start]) / data['Close'][start])
    print('Benchmark : %.2f%% %s to %s' % 
          (bench, data.index[start].strftime("%m-%d-%y"), data.index[-1].strftime("%m-%d-%y")))
    for strategy in strategy_list:      
        strategy.report()
        
    return
    