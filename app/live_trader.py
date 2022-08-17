#
# Created on Wed Aug 10 2022
#
# Copyright (c) 2022 H. Alterman
#

import alpaca_trade_api as tradeapi
from datetime import datetime,timezone, timedelta
import indicators
import pandas as pd
import logging
import time
import json
from alpaca_trade_api.common import URL
import threading
import asyncio
import yfinance as yf
from decimal import *
import os
import sys
import pytz
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO


dirname = os.path.dirname(__file__)


logging.basicConfig(filename='app_logs.log',
         format='%(asctime)s %(message)s', 
         level=logging.INFO, filemode = 'w') 
#logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))     
#Bar intervals for prices
interval = '1m'


# API Info for fetching data, portfolio, etc. from Alpaca
print('beginning live trade')
#get keys from json file
with open(os.path.join(dirname,'alpaca_keys.json'), 'r') as f:
  alpaca_keys = json.load(f)
BASE_URL = alpaca_keys['BASE_URL']
ALPACA_API_KEY = alpaca_keys['ALPACA_API_KEY']
ALPACA_SECRET_KEY = alpaca_keys['ALPACA_SECRET_KEY']
curr_datetime = datetime.now(timezone.utc)

class live_trader(object):
    ################################################################################
    #live trader class to use pre-trained model against 
    #Alpaca trading environment.
    #Trades on a single ticker defined on initialization.
    #Can be initialize with
    #1.symbol - stock ticker we are trading
    #2.order_size - The learner only determines hold a long,short or no position order size determines
    #   how large each order should be. Should be the same size used in max_trade of the training enironment
    ###############################################################################

    def __init__(self,
          
    
                symbol = 'AAPL', 
                order_size = 60,               
                ttc = 9999):

        newYorkTz = pytz.timezone("America/New_York") 
        self.curr_datetime = datetime.now(newYorkTz)
        self.api = tradeapi.REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, 
                            base_url=BASE_URL, api_version='v2')
        self.timeToClose = 9999
        self.symbol = symbol
        self.order_size = order_size
        self.close_prices = [159.59, 159.595, 159.54, 159.52, 159.6, 159.575, 159.5, 159.49, 159.315, 159.47, 159.645, 159.75, 159.765, 159.56, 159.595, 159.67, 159.655, 159.55, 159.425,]
        self.SPY_prices = [159.59, 159.595, 159.54, 159.52, 159.6, 159.575, 159.5, 159.49, 159.315, 159.47, 159.645, 159.75, 159.765, 159.56, 159.595, 159.67, 159.655, 159.55, 159.425,]

        self.count_of_prices_to_retain = 10
        self.model = PPO.load("ppo_trader")
        dirname = os.path.dirname(__file__)


        logging.basicConfig(filename='{}_app_logs.log'.format(symbol),
            format='%(asctime)s %(message)s', 
            level=logging.INFO, filemode = 'w') 

    def get_interval_as_int(self,interval:str) -> int:
        #########################################################
        #utility to convvert the yfinance bar intervals to
        #seconds interget
        #########################################################
        seconds_per_unit = {"m": 60, "h": 3600, "d": 86400, "w": 604800}
        return int(interval[:-1]) * seconds_per_unit[interval[-1]]


    def calculate_indicators(self,prices:pd.DataFrame,symbol:str,spy_prices:pd.Series) -> pd.DataFrame:
        #########################################################
        #calculate indicators using indicator functions
        #return a dataframe that can be used with StableBaseline3
        #########################################################
        df = prices
        #print(prices)
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

    def get_current_position(self)->int:
        #########################################################
        #query Alpaca API
        #########################################################
        try:
            current_position = int(self.api.get_position(symbol = self.symbol).qty)
        except tradeapi.rest.APIError:
            logging.info(tradeapi.rest.APIError)
            logging.info('No current position')
            current_position = 0   
        return current_position

    def query_model(self,obs,position):
        action, _states = self.model.predict(obs)
        #action is int 0 through 2. subtract 1 so we have -1 through 1
        #multiply by order size for target position
        target_position = ((action-1) * self.order_size)
        
        return target_position

    def consumer_thread(self):
        ######################################################################
        #main loop to iteratively download latest data and take action.
        ######################################################################

        
        while(self.timeToClose>1):
            #download data from y finance
            NewYorkTz = pytz.timezone("America/New_York") 
            curr_datetime = datetime.now(NewYorkTz)
            df = yf.download([self.symbol,'SPY'],start = curr_datetime - timedelta(minutes=30), end = curr_datetime, interval='1m',progress=False,rounding=True)
            if len(df)< 5:
                logging.warning('Not enough data in last 30 minutes to calculate indicators')
            else:
                self.close_prices = pd.DataFrame()
                self.close_prices[self.symbol] = df['Adj Close',self.symbol].fillna(method='ffill')

                
                self.SPY_prices = df['Adj Close','SPY']
                self.SPY_prices.fillna(method='ffill')
                
                #query learner and execute appropriate action
                self.execute_QAction()
                #depending on what interval we trained on are using we will wait at least half that time until querying the learner again
                interval_in_seconds = self.get_interval_as_int(interval)
                time.sleep(interval_in_seconds/2)





    def execute_QAction(self):
        ######################################################################
        #queries the learner to determine an action to take 
        #and execute that action
        ######################################################################

        #Get the difference between current and target position
        logging.debug('get_Qaction prices: '.format(self.close_prices))
        logging.debug(self.close_prices)
        current_position = 0
        
        current_position = self.get_current_position()
  
     
       
        logging.debug(self.close_prices)
        ind_df = self.calculate_indicators(prices = self.close_prices, 
                                           symbol=self.symbol,
                                           spy_prices = self.SPY_prices)
        current_datetime = ind_df.index[-1]
        ind_df.loc[current_datetime,'position'] = current_position
        obs = ind_df.loc[current_datetime].to_numpy()
        target_position = self.query_model(obs=obs,position = current_position)

        logging.info('Target: {}'.format(target_position))
        
       
        difference_between_target = int(target_position - current_position)
        switching_long_short = (target_position*current_position) <0
   
        transaction_quantity = abs(difference_between_target)

        logging.debug(self.close_prices)
        limit = self.close_prices[self.symbol][-1]
        #if we are not at our position cancel existing trades and make a trade to achieve desired position
        if difference_between_target != 0:
            if self.is_EOD():
                self.close_all_positions_at_eod()
            else:
                #if we are switching between long and short positions we must first clear our position. because alpaca friggin blow
                if switching_long_short:
                    
                    try:
                        current_position = int(self.api.get_position(symbol = self.symbol).qty)
                    except tradeapi.rest.APIError:
              
                        logging.warning(tradeapi.rest.APIError)
                        current_position = 0
                    difference_between_target = 0 - current_position
                    thread_zero_out = threading.Thread(target=self.zero_out_before_position,
                    args=[limit,difference_between_target])
                    thread_zero_out.start()
                    thread_zero_out.join()
                else:
                    logging.info('submitting order for : {}'.format(difference_between_target))
                    logging.info('submitting order for : {}'.format(difference_between_target))
                    logging.info('Raw limit price: {}'.format(limit))
                    logging.info('limit price : {}'.format(float(str(round(limit, 2)))))
                    difference_between_target = int(target_position - current_position)
                    transaction_quantity = abs(difference_between_target)
                    #create a new order
                    order_type = "sell" if difference_between_target < 0 else 'buy'
                    status = 'none'
                    max_retries = self.get_interval_as_int(interval)/2
                    retries  = 0
                    
                    #while the order isn't filled retry placing the order up to 30 times
                    while status.lower() != 'filled' and retries < max_retries:
                        logging.info('retry: {}'.format(retries))
                        retries += 1
                        try:
                            #try to submit order catch any api error and print try zeroing out order and retry
                            order = self.api.submit_order(
                                    symbol=self.symbol,
                                    qty=transaction_quantity,
                                    side=order_type,
                                    type='limit',
                                    time_in_force='ioc',
                                    limit_price=float(str(round(limit, 2)))
                                    
                                    )
                            #sleep for a second to wait for the order to either go through or cancel
                            time.sleep(1)
                            #if the order was successful set status to break loop
                            last_order_id = order.id
                            order = self.api.get_order(last_order_id)
                            status = order.status           
                        except tradeapi.rest.APIError:
                            status = 'failed'
                            #catch api exception try to zero out position
                            
                            logging.warning(tradeapi.rest.APIError)
                            current_position = self.get_current_position()
                            #if we have a position, try zeroing it out
                            if current_position != 0:
                                logging.info('Zeroing out position')
                                difference_between_target = 0 - current_position
                                thread_zero_out = threading.Thread(target=self.zero_out_before_position,
                                args=[limit,difference_between_target])
                                thread_zero_out.start()
                                thread_zero_out.join()

                            
                            

                
                        
                        
                        print(status)


    def zero_out_before_position(self,limit:float,difference_between_target:float=0):
        ######################################################################
        #Due to alpaca limitations positions must be zeroed out before moving
        #long short. Short function to zero out the function
        #####################################################################
   
        order_type = "sell" if difference_between_target < 0 else 'buy'
        logging.info('zero out position: submitting order for : {}'.format(difference_between_target))
        transaction_quantity = abs(difference_between_target)
        status = 'none'
        retries = 0
        #try zeroing out three times before giving up
        while status.lower() != 'filled' and retries <3:
            logging.info('retries: {}'.format(retries))
            retries +=1
            order = self.api.submit_order(
                symbol=self.symbol,
                qty=transaction_quantity,
                side=order_type,
                type='limit',
                time_in_force='ioc',
                limit_price=float(str(round(limit, 2)))
                )
            
            
            
            if retries >= 3:
                logging.info('limit order failed submitting market')
                order = self.api.submit_order(
                symbol=self.symbol,
                qty=transaction_quantity,
                side=order_type,
                type='market',
                )
            time.sleep(1)
            last_order_id = order.id
            order = self.api.get_order(last_order_id)
            status = order.status
            logging.info('order status: {}'.format(order.status))

        
         
            


    def is_EOD(self)->bool:
        ######################################################################
        #check if we are 5 minutes from close of trading
        #####################################################################
        minutes_before_close = 5
        clock = self.api.get_clock()
        closingTime = clock.next_close.replace(tzinfo=timezone.utc).timestamp()
        currTime = clock.timestamp.replace(tzinfo=timezone.utc).timestamp()
        self.timeToClose = closingTime - currTime
        return self.timeToClose < (60 * minutes_before_close)
    def close_all_positions_at_eod(self):
        
        # Close all positions when 5 minutes til market close.
        logging.info("Market closing soon.  Closing positions.")

        position = self.api.get_position(symbol = self.symbol)
        
        if(position > 0):
            orderSide = 'sell'
        elif (position < 0):
            orderSide = 'buy'
        qty = abs(int(float(position.qty)))
        respSO = []
        status = 'unsubmitted'

        if position !=0:
            while status.lower() != 'filled':
                order = self.api.submitorder(qty=qty, symbol = self.symbol,
                    side= orderSide,
                    type = 'market')
                time.sleep(1)
                last_order_id = order.id
                order = self.api.get_order(last_order_id)
                status = order.status
                
            




    




