#
# Created on Wed Aug 10 2022
#
# Copyright (c) 2022 H. Alterman
#

import train_gym
import alpaca_trade_api as tradeapi
from datetime import datetime,timezone, timedelta
import pandas as pd
import live_trader
import threading
import time
import logging
import sys
import os
import json

#configure logs
logging.basicConfig(filename='app_logs.log',
         format='%(asctime)s %(message)s', 
         level=logging.INFO, filemode = 'w')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
# API Info for fetching data, portfolio, etc. from Alpaca
print('start')
pd.set_option('display.max_rows', 100)
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname,'alpaca_keys.json'), 'r') as f:
  alpaca_keys = json.load(f)
BASE_URL = alpaca_keys['BASE_URL']
ALPACA_API_KEY = alpaca_keys['ALPACA_API_KEY']
ALPACA_SECRET_KEY = alpaca_keys['ALPACA_SECRET_KEY']
curr_datetime = datetime.now(timezone.utc)


def awaitMarketOpen():
    ####################################################
    #loop to check if market has opened
    ###################################################
    isOpen = api.get_clock().is_open
    while(not isOpen):
      clock = api.get_clock()
      openingTime = clock.next_open.replace(tzinfo=timezone.utc).timestamp()
      currTime = clock.timestamp.replace(tzinfo=timezone.utc).timestamp()
      timeToOpen = int((openingTime - currTime) / 60)
      logging.debug(str(timeToOpen) + " minutes til market open.")
      print(str(timeToOpen) + " minutes til market open.")
      time.sleep(60)
      isOpen = api.get_clock().is_open
  
def run_awaitMarketOpen():
    ####################################################
    #creates thread to pause execution until market opens
    ###################################################
    print("Waiting for market to open...")
    tAMO = threading.Thread(target=awaitMarketOpen)
    tAMO.start()
    tAMO.join()
    print("Market opened")

def train(symbol):
    ####################################################
    #creates thread to pause execution until market opens
    ###################################################
    train_gym.get_and_clean_data(symbol=symbol)
    prices = train_gym.get_and_clean_data()
    spy = train_gym.get_SPY_data()
    ind_df = train_gym.calculate_indicators(prices = prices, symbol='AAPL',spy_prices = spy)
    print(ind_df)
    model, env = train_gym.trainmodel(prices,indicators= ind_df)
    return model,env


if __name__ == '__main__':
    symbol = 'AAPL'
    if len(sys.argv)>1:
        symbol = sys.argv[1]
    model,env = train(symbol)
    #run_awaitMarketOpen()
    trader = live_trader.live_trader(symbol = symbol)
    trader.consumer_thread()