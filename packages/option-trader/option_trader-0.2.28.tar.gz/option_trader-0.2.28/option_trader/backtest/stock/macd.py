
import numpy as np

def MACD_color(data):
    MACD_color = []
    for i in range(0, len(data)):
        if data['MACDh_12_26_9'][i] > data['MACDh_12_26_9'][i - 1]:
            MACD_color.append(True)
        else:
            MACD_color.append(False)
    return MACD_color

def MACD_strategy(data,stop_gain=20, stop_loss=20):

    #print('MACD_strategy')
    
    Buy=[]
    Sell=[]
    Profit=[]
    
    position=False

    last_buy = np.nan
    last_sell = np.nan
    
    initial_cost = 0
    total_profit = 0
    
    for i in range(0, len(data)):
        if data['MACD_12_26_9'][i] > data['MACDs_12_26_9'][i] :
            Sell.append(np.nan)
            if position ==False:
                Buy.append(data['Close'][i])
                last_buy = i
                if initial_cost == 0:
                    initial_cost  = data['Close'][i]
                position=True
            else:
                Buy.append(np.nan)
        elif data['MACD_12_26_9'][i] < data['MACDs_12_26_9'][i] :
            Buy.append(np.nan)
            if position == True:
                Sell.append(data['Close'][i])
                last_sell = i
                total_profit += data['Close'][i] - data['Close'][last_buy]
                position=False
            else:
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
        else:
            Buy.append(np.nan)
            Sell.append(np.nan)

        Profit.append(total_profit) 
                
    data['MACD_Buy_Signal_price'] = Buy
    data['MACD_Sell_Signal_price'] = Sell
    data['MACD_positive'] = MACD_color(data)  
    if initial_cost > 0:
        Profit = (Profit / initial_cost) * 100        
    data['MACD_profit'] = Profit
    
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
    #    print('MACD Inital cost =' + str(initial_cost) + ' profit=' + str((total_profit/initial_cost)*100))
    #else:
    #    print('No MACD transaction')

    return last_action, last_price, recent, total_profit
    
import matplotlib.pyplot as plt

from option_trader.settings import app_settings  as settings    
from option_trader.settings import ta_strategy  as  ta  


def plot_MACD(symbol, data):
    
    if 'MACD_12_26_9' not in data:
        data.ta.cores = 2
        data.ta.strategy(ta.CustomStrategy)
        
    if 'MACD_Buy_Signal_price' not in data:
        MACD_strategy(data)
    
    plt.rcParams.update({'font.size': 10})
    fig, axx = plt.subplots(figsize=(10,8))
    fig.suptitle(symbol + " [MACD]", fontsize=30)
    ax1 = plt.subplot2grid((24, 8), (0, 0), rowspan=8, colspan=14)

    ax1.set_ylabel('Price')
    ax1.plot('Close',data=data, linewidth=0.5, color='blue')
    ax1.scatter(data.index, data['MACD_Buy_Signal_price'], color='green', marker='^', alpha=1)
    ax1.scatter(data.index, data['MACD_Sell_Signal_price'], color='red', marker='v', alpha=1)
    ax1.legend()
    ax1.grid()
    #ax1.set_xlabel('Date', fontsize=8)

    ax2 = plt.subplot2grid((24, 12), (10, 0), rowspan=6, colspan=14, sharex=ax1)
    ax2.set_ylabel('MACD', fontsize=8)
    ax2.plot('MACD_12_26_9', data=data, label=symbol, linewidth=0.5, color='blue')
    ax2.plot('MACDs_12_26_9', data=data, label='signal', linewidth=0.5, color='red')
    ax2.bar(data.index,'MACDh_12_26_9', data=data, label='Histogram', color=data.MACD_positive.map({True: 'g', False: 'r'}),width=1,alpha=0.8)
    ax2.axhline(0, color='black', linewidth=0.5, alpha=0.5)
    ax2.grid()
    
    #ax3 = plt.subplot2grid((24,12), (18, 0), rowspan=6, colspan=14, sharex=ax1)
    #ax3.set_ylabel('MACD profit')
    #ax3.plot('MACD_profit',data=data, label=symbol, linewidth=0.5, color='blue')
    #ax3.legend()
    #ax3.grid()
    
    output_path = settings.CHART_ROOT_DIR + '/' + symbol+'_MACD.png'
    plt.savefig(output_path, bbox_inches='tight')       

    plt.close() 

    return output_path
