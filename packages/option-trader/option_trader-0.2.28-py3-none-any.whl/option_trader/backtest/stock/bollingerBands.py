import numpy as np

# trigger - percentage of gap to buy/sell
# stop_gain - profit taking percent
# stop_loss - stop loss percent

def BB_strategy(data, trigger = 0, stop_gain=20, stop_loss=20, window_size=7):
        
    Buy = []
    Sell = []
    Profit = []
    
    position = False
 
    data.dropna(subset=["BBL_20_2.0"])
    
    initial_cost = 0
    total_profit = 0
    
    last_buy = np.nan
    last_sell = np.nan
    
    for i in range(len(data)):
    
        s = window_size # sample size for Mann-Kendall Trend Test
        gfg_data = [0] * s

        # perform Mann-Kendall Trend Test   
        last_date_index = len(data.index)-1        
        for j in range(s):        
            gfg_data[j] = data['BBM_20_2.0'][last_date_index-s+1+j]    

        buy_trigger = trigger *  data['BBL_20_2.0'][i]
    
        sell_trigger = trigger *  data['BBU_20_2.0'][i]
    
        if data['Close'][i] - buy_trigger < data['BBL_20_2.0'][i]:
            if position == False :
                Buy.append(data['Close'][i])
                last_buy = i
                Sell.append(np.nan)
                if initial_cost == 0:
                    initial_cost = data['Close'][i]

                position = True
            else:
                Buy.append(np.nan)
                Sell.append(np.nan)
        elif data['Close'][i] + sell_trigger > data['BBU_20_2.0'][i]:
            if position == True:
                Buy.append(np.nan)
                Sell.append(data['Close'][i])
                last_sell = i
                position = False #To indicate that I actually went there
                total_profit += data['Close'][i] - data['Close'][last_buy]          
            else:
                Buy.append(np.nan)
                Sell.append(np.nan)
        elif position == True:
            diff = 100 * (abs(data['Close'][i] - data['Close'][last_buy]) / data['Close'][last_buy])
            if (data['Close'][i] > data['Close'][last_buy] and diff > stop_gain) or (data['Close'][i] < data['Close'][last_buy] and diff > stop_loss):                 
                Sell.append(data["Close"][i])
                last_sell = i
                total_profit += data['Close'][i] - data['Close'][last_buy]  
                position = False                  
            else:
                Sell.append(np.nan)            
            Buy.append(np.nan)
        else :
            Buy.append(np.nan)
            Sell.append(np.nan)
            
        Profit.append(total_profit) 

    data['BB_Buy_Signal_price'] = Buy
    data['BB_Sell_Signal_price'] = Sell
    if initial_cost > 0:
        Profit = (Profit / initial_cost) * 100
    data['BB_profit'] = Profit

    last_action = ''
    last_price = np.nan
    recent = False
    
    if last_buy > last_sell:   
        last_action = 'Buy'
        last_price = data["Close"][last_buy]
        if len(data) - last_buy  < 3:
            recent = True    
            
    elif last_sell > last_buy:
        last_action = 'Sell'
        last_price = data["Close"][last_sell]
        if len(data) - last_sell  < 3:
            recent = True
            
    #if initial_cost > 0:
    #    print('BB Inital cost =' + str(initial_cost) + ' profit=' + str((total_profit/initial_cost)*100))
    #else:
    #    print('No BB transaction')
        
    return last_action, last_price, recent, total_profit

import matplotlib.pyplot as plt
from option_trader.settings import ta_strategy  as  ta  

def plot_BB(symbol, data):    

    if 'BBM_20_2.0' not in data:
        data.ta.cores = 2
        data.ta.strategy(ta.CustomStrategy)
        
    if 'BB_Buy_Signal_price' not in data:
        BB_strategy(data)

    plt.rcParams.update({'font.size': 10})        
    fig, axx = plt.subplots(figsize=(10,8))
    fig.suptitle(symbol + "[Bollinger band]", fontsize=30)
    #ax1.remove()
    ax1 = plt.subplot2grid((24, 8), (0, 0), rowspan=8, colspan=14)   

    ax1.set_ylabel('Price in ₨')
    #ax1.set_xlabel('Date', fontsize=8)

    ax1.plot(data['Close'],label='Price', linewidth=1.2, color='black')
    ax1.plot(data['BBM_20_2.0'], label='Middle', color='blue', alpha=0.35) #middle band
    ax1.plot(data['BBU_20_2.0'], label='Upper', color='green', alpha=0.35) #Upper band  
    ax1.plot(data['BBL_20_2.0'], label='Lower', color='red', alpha=0.35) #Upper band      

    ax1.scatter(data.index, data['BB_Buy_Signal_price'], color='green', marker='^', alpha=1)
    ax1.scatter(data.index, data['BB_Sell_Signal_price'], color='red', marker='v', alpha=1)

    ax1.legend(['Price', 'Middle', 'Upper', 'Lower', 'Buy', 'Sell'], loc ="lower left")

    ax1.grid()

    ax2 = plt.subplot2grid((24, 12), (10, 0), rowspan=6, colspan=14, sharex=ax1)
    ax2.bar(data.index,'Volume', data=data, label='Volume',width=1,alpha=0.8)    
    ax2.grid()

    '''    
    ax3 = plt.subplot2grid((24,12), (18, 0), rowspan=6, colspan=14, sharex=ax1)
    ax3.set_ylabel('BB profit')
    ax3.plot('BB_profit',data=data, label='BB profit', linewidth=0.5, color='blue')
    #ax3.legend()
    ax3.grid()
    '''
    from option_trader.settings import app_settings  as settings    
    from option_trader.settings import ta_strategy  as  ta  

    output_path =  settings.CHART_ROOT_DIR + '/' + symbol+'_BB.png'

    plt.savefig(output_path, bbox_inches='tight')       

    #plt.show()    

    plt.close() 

    return output_path