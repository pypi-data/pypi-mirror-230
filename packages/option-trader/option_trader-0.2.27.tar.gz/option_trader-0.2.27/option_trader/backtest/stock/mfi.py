
import numpy as np

def MFI_strategy(data, BuyLvl=30, SellLvl=70, stop_gain=20, stop_loss=20):

    #print('MFI_strategy')
        
    Buy = []
    Sell = []
    Profit = []
    
    position = False
 
    data.dropna(subset=["MFI_14"])
    
    initial_cost = 0
    total_profit = 0
    
    last_buy = np.nan
    last_sell = np.nan

    for i in range(len(data)):
        if data['MFI_14'][i] < BuyLvl:
            if position == False :
                Buy.append(data['Close'][i])
                Sell.append(np.nan)              
                if initial_cost == 0:
                    initial_cost = data['Close'][i]
                last_buy = i
                #print('Buy at ' + str(last_buy_price) + 'MFI=' + str(data['MFI_14'][i]))
                position = True
            else:
                Buy.append(np.nan)
                Sell.append(np.nan)
        elif  data['MFI_14'][i] > SellLvl:
            if position == True:
                Buy.append(np.nan)
                Sell.append(data['Close'][i])
                last_sell = i
                total_profit += (data['Close'][i]-data['Close'][last_buy])
                position = False      
            else:
                Buy.append(np.nan)
                Sell.append(np.nan)
        elif position == True:
            diff = abs(data['Close'][i] - data['Close'][last_buy]) / data['Close'][last_buy]
            if (data['Close'][i] > data['Close'][last_buy] and diff * 100 > stop_gain) or (data['Close'][i] < data['Close'][last_buy] and diff > stop_loss):
                Sell.append(data["Close"][i])
                last_sell = i
                total_profit += (data['Close'][i]-data['Close'][last_buy])
                position = False   
            else:
                Sell.append(np.nan)
            Buy.append(np.nan)
        else :
            Buy.append(np.nan)
            Sell.append(np.nan)
            
        Profit.append(total_profit) 

    data['MFI_Buy_Signal_price'] = Buy
    data['MFI_Sell_Signal_price'] = Sell
    
    if initial_cost > 0:
        Profit = (Profit / initial_cost) * 100
        
    data['MFI_profit'] = Profit

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
    #    print('MFI Inital cost =' + str(initial_cost) + ' profit=' + str((total_profit/initial_cost)*100))
    #else:
    #    print('No MFI transaction')
        
    return last_action, last_price, recent, total_profit


import matplotlib.pyplot as plt

from option_trader.settings import app_settings  as settings    
from option_trader.settings import ta_strategy  as  ta 

def plot_MFI(symbol, data):

    if 'MFI_14' not in data:
        data.ta.cores = 2
        data.ta.strategy(ta.CustomStrategy)
        
    if 'MFI_Buy_Signal_price' not in data:
        MFI_strategy(data)
        
    #define width of candlestick elements
    width = .4
    width2 = .05

    #define up and down prices
    up = data[data.Close>=data.Open]
    down = data[data.Close<data.Open]

    #define colors to use
    col1 = 'green'
    col2 = 'red'

    #create figure 
    plt.rcParams.update({'font.size': 10})
    fig, axx = plt.subplots(figsize=(10,8))
    fig.suptitle(symbol + " [MFI]", fontsize=30)
    ax1 = plt.subplot2grid((24, 8), (0, 0), rowspan=8, colspan=14)

    #plot up prices
    ax1.bar(up.index,up.Close-up.Open,width,bottom=up.Open,color=col1)
    ax1.bar(up.index,up.High-up.Close,width2,bottom=up.Close,color=col1)
    ax1.bar(up.index,up.Low-up.Open,width2,bottom=up.Open,color=col1)

    #plot down prices
    ax1.bar(down.index,down.Close-down.Open,width,bottom=down.Open,color=col2)
    ax1.bar(down.index,down.High-down.Open,width2,bottom=down.Open,color=col2)
    ax1.bar(down.index,down.Low-down.Close,width2,bottom=down.Close,color=col2)

    ax1.scatter(data.index, data['MFI_Buy_Signal_price'], color='green', marker='^', alpha=1)
    ax1.scatter(data.index, data['MFI_Sell_Signal_price'], color='red', marker='v', alpha=1)

    #ax1.legend()
    ax1.grid()

    ax2 = plt.subplot2grid((24, 12), (10, 0), rowspan=6, colspan=14, sharex=ax1)
    ax2.set_ylabel('MFI')
    ax2.plot('MFI_14',data=data, label=symbol, linewidth=0.5, color='blue')
    #ax2.legend()
    ax2.grid()
    
    #ax3 = plt.subplot2grid((24, 12), (18, 0), rowspan=6, colspan=14, sharex=ax1)
    #ax3.set_ylabel('Profit')
    #ax3.plot('MFI_profit',data=data, label=symbol, linewidth=0.5, color='blue')
    #ax3.legend()
    #ax3.grid()

    output_path = settings.CHART_ROOT_DIR+ '/' + symbol+'_MFI.png'
  
    plt.savefig(output_path, bbox_inches='tight')       

    plt.close() 

    return output_path