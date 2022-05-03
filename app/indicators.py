
import pandas as pd
import datetime as dt 
import numpy as np
def run_bollinger(price_df,symbol):
    df = price_df
    df[symbol+'_SMA'] = df.iloc[:,0].rolling(window=10).mean()
    df[symbol+'_std'] = (df.iloc[:,0].rolling(window=10).std())*2
    df['top_band'] = df[symbol+'_SMA'] + df[symbol+'_std']
    df['bottom_band'] = df[symbol+'_SMA'] - df[symbol+'_std']
    df['previous_top'] =df['top_band'].shift(1)
    df['previous_bottom'] =df['bottom_band'].shift(1)
    df['previous price'] = df[symbol].shift(1)
    df['bbpercent'] = (df[symbol] - df['bottom_band'])/(df['top_band'] - df['bottom_band'])

    return df['bbpercent'] 

def run_SPY_Ratio(price_df,spy_price_series,symbol):
    ratio = price_df[symbol]/spy_price_series
    return ratio
def run_SMA(price_df, symbol):
    #print(symbol)
    df = price_df
    #3 day
    df[symbol+'_14SMA'] = df.iloc[:,0].rolling(window=7).mean()

    df['indicator'] = df[symbol]/df[symbol+'_14SMA']
    df['previous_indicator'] = df['indicator']
    df['previous_indicator'] = df['previous_indicator'].shift(1)

    df['trades'] = np.where((df['indicator']>1.05)  ,-1,0
    )
    df['trades'] = np.where((df['indicator']<.95) ,1,df.loc[df.index]['trades']
    )

    
    buy = df[df['trades']>1]
    sell = df[df['trades']<0]
    #print(df[['trades','indicator']].head(100))
   
    return df['indicator']
def run_momentum(price_df,symbol= 'AAPL',
    N = 7):
    #print('run momentum')
    df = price_df
    df[symbol+'_Momentum'] = df.iloc[:,0].rolling(window=7).mean()
    df['shifted'] = df[symbol].shift(N)
    df['momentum'] = (df[symbol]/ df['shifted']) -1
    df['momentum'] =df['momentum'].fillna(0)
    #print(df['momentum'])
    return df['momentum']
def run_stochasticos(price_df,symbol= 'AAPL'):
    df = price_df
    df['14-High'] = df[symbol].rolling(7).max()
    df['14-Low'] = df[symbol].rolling(7).min()
    df['K'] = (df[symbol] - df['14-Low'])/(df['14-High']-df['14-Low'])
    return df['K']



def author():
    return 'halterman3' 