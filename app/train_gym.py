from cgitb import reset
import trader_env
import indicators
import pandas as pd
import yfinance as yf
from datetime import datetime,timezone, timedelta
from setuptools import setup
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO

check_env(trader_env.StockTradeEnv())

curr_datetime = datetime.now(timezone.utc)
def get_and_clean_data(starttime = (curr_datetime - timedelta(days=10)).strftime('%Y-%m-%d'),
    endtime = (curr_datetime-timedelta(days=3)).strftime('%Y-%m-%d'), symbol = 'AAPL'):
    #get data from Alpaca API
    
    DATA = yf.download(symbol,
     start=starttime, end=endtime,interval='1m',rounding = True)
    DATA[symbol] = DATA.Close.fillna(method = 'ffill')   
    return pd.DataFrame(DATA[symbol])
def get_SPY_data (starttime = (curr_datetime - timedelta(days=14)).strftime('%Y-%m-%d'),
                    endtime = (curr_datetime-timedelta(days=3)).strftime('%Y-%m-%d')):

    DATA = yf.download("SPY",
     start=starttime, end=endtime,interval='1m',rounding = True)
    DATA["SPY"] = DATA.Close.fillna(method = 'ffill')
    return DATA["SPY"]

def calculate_indicators(prices,symbol,spy_prices):
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
def trainmodel(prices,indicators):
    env = trader_env.StockTradeEnv(price_df=prices,indicator_df=indicators,observation_shape=(indicators.shape[1],))
    model = PPO("MlpPolicy", env, verbose=1)
    obs = env.reset()
    model.learn(total_timesteps = 6000)
    # for i in range(1000):
    #     action, _state = model.predict(obs, deterministic=True)
    #     obs, reward, done, info = env.step(action)
    
    model.save("ppo_trader")
    return model, env

def testmodel(prices,indicators,env):
    env = trader_env.StockTradeEnv(price_df=prices,indicator_df=indicators,observation_shape=(indicators.shape[1],))
    model = PPO.load("ppo_trader")
    #test using new prices and indicators
    setattr(env,'price_df',prices)
    setattr(env,'indicator_df',indicators)

    obs = env.reset()
    reward_sum = 0
    for i in range(len(prices.index)):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        reward_sum += rewards
        print('reward:{}   total reward:{}  '.format(rewards,reward_sum))

    print('total reward: {}'.format(reward_sum))



if __name__ == '__main__':
    #Train
    prices = get_and_clean_data()
    spy = get_SPY_data()
    ind_df = calculate_indicators(prices = prices, symbol='AAPL',spy_prices = spy)
    print(ind_df)
    model, env = trainmodel(prices,indicators= ind_df)

    #Test
    prices = get_and_clean_data(starttime = (curr_datetime - timedelta(days=3)).strftime('%Y-%m-%d'),
                                endtime = (curr_datetime-timedelta(days=0)).strftime('%Y-%m-%d'), 
                                symbol = 'AAPL')
    spy = get_SPY_data (starttime = (curr_datetime - timedelta(days=3)).strftime('%Y-%m-%d'),
                        endtime = (curr_datetime-timedelta(days=0)).strftime('%Y-%m-%d'))
    ind_df = calculate_indicators(prices = prices, symbol='AAPL',spy_prices = spy)
    testmodel(prices,indicators= ind_df, env = env)
    




