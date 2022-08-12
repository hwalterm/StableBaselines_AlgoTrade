#
# Created on Wed Aug 10 2022
#
# Copyright (c) 2022 H. Alterman
#

from cgitb import reset
import trader_env
import indicators
import pandas as pd
import yfinance as yf
from datetime import datetime,timezone, timedelta
from setuptools import setup
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO
import logging
import os
import json
from alpha_vantage.timeseries import TimeSeries

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname,'alpaca_keys.json'), 'r') as f:
  alpaca_keys = json.load(f)
ALPHAV_KEY = alpaca_keys['ALPHA_V']

interval = '1m'
check_env(trader_env.StockTradeEnv())
curr_datetime = datetime.now(timezone.utc)


def get_and_clean_data(starttime:str = (curr_datetime - timedelta(days=14)).strftime('%Y-%m-%d'),
    endtime:str = (curr_datetime-timedelta(days=0)).strftime('%Y-%m-%d'), symbol = 'AAPL')->pd.DataFrame:
    ####################################################
    #retrieve prices data from yfinance for given symbol
    #Expects: 
    # 1.start and end dates as string format yyy-mm-dd
    # 2.ticker symbol as string
    ###################################################
    #get data from ALPHAV api
    
    # DATA = yf.download(symbol,
    #  start=starttime, end=endtime,interval=interval,rounding = True)
    
    ts = TimeSeries(key=ALPHAV_KEY,output_format='pandas', indexing_type='date')
    DATA,meta= ts.get_intraday(symbol = symbol,interval = '1min',outputsize='full')
    DATA.rename({'4. close':'Close','date':'Datetime'}, axis =1, inplace = True)
    DATA[symbol] = DATA.Close.fillna(method = 'ffill')  
    
    return pd.DataFrame(DATA[symbol])
def get_SPY_data (starttime = (curr_datetime - timedelta(days=14)).strftime('%Y-%m-%d'),
                    endtime = (curr_datetime-timedelta(days=0)).strftime('%Y-%m-%d')):
    ####################################################
    #retrieve prices data from yfinance for given symbol
    #Expects: 
    # 1.start and end dates as string format yyy-mm-dd
    ###################################################
    ts = TimeSeries(key=ALPHAV_KEY,output_format='pandas', indexing_type='date')
    DATA,meta= ts.get_intraday(symbol = "SPY",interval = '1min',outputsize='full')
    DATA.rename({'4. close':'Close','date':'Datetime'}, axis =1, inplace = True)
    DATA["SPY"] = DATA.Close.fillna(method = 'ffill')  

    # DATA = yf.download("SPY",
    #  start=starttime, end=endtime,interval=interval,rounding = True)
    # DATA["SPY"] = DATA.Close.fillna(method = 'ffill')
    return DATA["SPY"]

def calculate_indicators(prices:pd.DataFrame,symbol:str,spy_prices:pd.Series)->pd.DataFrame:
    ####################################################
    #calculate indicators for prices dataframe
    #Expects: 
    # 1.Prices dataframe with the [symbol] column containing close prices
    # 2.the S&P500 close prices series in the spy_prices dataframe(for calculating spy ratio)
    # 3.the ticker symbol
    ###################################################
    df = prices
    df['sma'] = indicators.run_SMA(prices,symbol=symbol)
    df['momentum'] = indicators.run_momentum(prices,symbol=symbol)
    df['stochasticos'] = indicators.run_stochasticos(prices,symbol=symbol)
    df['bollinger'] = indicators.run_bollinger(prices,symbol=symbol)	
    df['SPY_Ratio'] = indicators.run_SPY_Ratio(prices,spy_price_series=spy_prices,symbol=symbol)
    #always initialize current position to 0
    df['position'] = 0
    df = df[['sma','momentum','stochasticos','SPY_Ratio','position']]
    df = df.fillna(0)
    return df
def trainmodel(prices:pd.DataFrame,indicators:pd.DataFrame):
    ####################################################
    #Train model using PPO
    ###################################################
    env = trader_env.StockTradeEnv(price_df=prices,indicator_df=indicators,observation_shape=(indicators.shape[1],))
    model = PPO("MlpPolicy", env, verbose=1,
     #gamma = .9999,learning_rate=0.00001
     )
    obs = env.reset()
    model.learn(total_timesteps = 90000)
    # for i in range(1000):
    #     action, _state = model.predict(obs, deterministic=True)
    #     obs, reward, done, info = env.step(action)
    
    model.save("ppo_trader")
    return model, env

def testmodel(prices,indicators,env):
    ####################################################
    #Test model against test data Expects
    #1. Prices dataframe 
    #2. indicator dataframe
    #3.Training environment. Should point to same environment that data was trained on
    ###################################################

    logging.info('testing')
    env = trader_env.StockTradeEnv(price_df=prices,indicator_df=indicators,observation_shape=(indicators.shape[1],))
    model = PPO.load("ppo_trader")
    #test using new prices and indicators
    setattr(env,'price_df',prices)
    setattr(env,'indicator_df',indicators)

    obs = env.reset()
    reward_sum = 0
    for i in range(len(prices.index)-1):
        action, _states = model.predict(obs)
        if prices.index[i].date()<prices.index[i+1].date():
            action = 1
        obs, rewards, dones, info = env.step(action)
        reward_sum += rewards
    #     print('reward:{}   total reward:{}  '.format(rewards,reward_sum))

    print('total reward: {}'.format(reward_sum))



if __name__ == '__main__':
    #Train
    prices = get_and_clean_data()
    spy = get_SPY_data()
    ind_df = calculate_indicators(prices = prices, symbol='AAPL',spy_prices = spy)
    print(ind_df)
    model, env = trainmodel(prices,indicators= ind_df)

    #Test
    prices = get_and_clean_data(starttime = (curr_datetime - timedelta(days=1)).strftime('%Y-%m-%d'),
                                endtime = (curr_datetime-timedelta(days=0)).strftime('%Y-%m-%d'), 
                                symbol = 'AAPL')
    spy = get_SPY_data (starttime = (curr_datetime - timedelta(days=1)).strftime('%Y-%m-%d'),
                        endtime = (curr_datetime-timedelta(days=0)).strftime('%Y-%m-%d'))
    ind_df = calculate_indicators(prices = prices, symbol='AAPL',spy_prices = spy)
    testmodel(prices,indicators= ind_df, env = env)
    




