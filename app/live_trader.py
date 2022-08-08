import alpaca_trade_api as tradeapi
import StrategyLearner as sl
from QLearner import QLearner
from marketsimcode import marketsim
from datetime import datetime,timezone, timedelta
import pandas as pd
import logging
import time
# from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
import threading
import asyncio
import yfinance as yf
from decimal import *
getcontext().prec = 2


# API Info for fetching data, portfolio, etc. from Alpaca
print('beginning live trade')
BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_API_KEY = "PKVH1SZ416UXYP2WMQDC"
ALPACA_SECRET_KEY = "RSuMJdSnBkHBpSxpWOiipyjTWOsqwgiPmBJYse3j"
curr_datetime = datetime.now(timezone.utc)

class live_trader(object):
    def __init__(self,
                learner,
                Qlearner,
                symbol = 'AAPL', 
                order_size = 60,               
                ttc = 9999):
        BASE_URL = "https://paper-api.alpaca.markets"
        ALPACA_API_KEY = "PKVH1SZ416UXYP2WMQDC"
        ALPACA_SECRET_KEY = "RSuMJdSnBkHBpSxpWOiipyjTWOsqwgiPmBJYse3j"
        self.curr_datetime = datetime.now(timezone.utc)
        self.api = tradeapi.REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, 
                            base_url=BASE_URL, api_version='v2')
        self.timeToClose = ttc
        self.symbol = symbol
        self.order_size = order_size
        self.close_prices = [159.59, 159.595, 159.54, 159.52, 159.6, 159.575, 159.5, 159.49, 159.315, 159.47, 159.645, 159.75, 159.765, 159.56, 159.595, 159.67, 159.655, 159.55, 159.425,]
        self.SPY_prices = [159.59, 159.595, 159.54, 159.52, 159.6, 159.575, 159.5, 159.49, 159.315, 159.47, 159.645, 159.75, 159.765, 159.56, 159.595, 159.67, 159.655, 159.55, 159.425,]
        self.learner = learner
        self.count_of_prices_to_retain = 10
        self.Qlearner = Qlearner
        QTable = Qlearner.Q
   

    def consumer_thread(self):
        
        while(self.timeToClose>1):
            df = yf.download(['AAPL','SPY'],period='1d', interval='1m',progress=False)
            self.close_prices = df['Adj Close','AAPL']
            self.SPY_prices = df['Adj Close','SPY']
            self.execute_QAction()





    def execute_QAction(self):

        #Get the difference between current and target position
        #print('get_Qaction prices: '.format(self.close_prices))
        #print(self.close_prices)
        current_position = 0
        mapped_position = 2
        try:
            current_position = int(self.api.get_position(symbol = self.symbol).qty)
        except tradeapi.rest.APIError:
            print(tradeapi.rest.APIError)
            current_position = 0
     
        #query the learner to get the prices
        if current_position > 0 :
            mapped_position = 1
        elif current_position < 0:
            mapped_position =0

        target_position = self.learner.query_for_live_data(prices = self.close_prices,
                                                 spy_prices = self.SPY_prices,
                                                 order_size = self.order_size,
                                                 symbol = self.symbol,
                                                 current_position = mapped_position
                                                 )

        #print('Target: {}'.format(target_position))
        
        print('target_position: {}'.format(target_position))
        difference_between_target = int(target_position - current_position)
        switching_long_short = (target_position*current_position) <0
   
        transaction_quantity = abs(difference_between_target)
        #print(self.close_prices[-10:])
        limit = self.close_prices.fillna(method='ffill')[ -1]
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
                        print(tradeapi.rest.APIError)
                        current_position = 0
                    difference_between_target = 0 - current_position
                    thread_zero_out = threading.Thread(target=self.zero_out_before_position,
                    args=[limit,difference_between_target])
                    thread_zero_out.start()
                    thread_zero_out.join()
                else:
                    print('submitting order for : {}'.format(difference_between_target))
                    print('Raw limit price: {}'.format(limit))
                    print('limit price : {}'.format(float(str(round(limit, 2)))))
                    difference_between_target = int(target_position - current_position)
                    transaction_quantity = abs(difference_between_target)
                    #create a new order
                    order_type = "sell" if difference_between_target < 0 else 'buy'
                    self.api.submit_order(
                            symbol=self.symbol,
                            qty=transaction_quantity,
                            side=order_type,
                            type='limit',
                            time_in_force='ioc',
                            limit_price=float(str(round(limit, 2)))
                            )
                    #sleep for a second to wait for the order to either go through or cancel
                    time.sleep(1)

           
    def zero_out_before_position(self,limit,difference_between_target=0,
                                    ):
   
        order_type = "sell" if difference_between_target < 0 else 'buy'
        print('zero out position: submitting order for : {}'.format(difference_between_target))
        transaction_quantity = abs(difference_between_target)
        self.api.submit_order(
            symbol=self.symbol,
            qty=transaction_quantity,
            side=order_type,
            type='limit',
            time_in_force='ioc',
            limit_price=float(str(round(limit, 2)))
            )
        time.sleep(1)
        
         
            


    def is_EOD(self):
        minutes_before_close = 5
        clock = self.api.get_clock()
        closingTime = clock.next_close.replace(tzinfo=timezone.utc).timestamp()
        currTime = clock.timestamp.replace(tzinfo=timezone.utc).timestamp()
        self.timeToClose = closingTime - currTime
        return self.timeToClose < (60 * minutes_before_close)
    def close_all_positions_at_eod(self):
        
        # Close all positions when 5 minutes til market close.
        print("Market closing soon.  Closing positions.")

        position = int(self.api.get_position(symbol = self.symbol))
        
        if(position.side == 'long'):
            orderSide = 'sell'
        else:
            orderSide = 'buy'
        qty = abs(int(float(position.qty)))
        respSO = []
        self.api.submitorder(qty=qty, symbol = position.symbol,
            side= orderSide,
            type = 'market')



        
    def get_and_clean_data(starttime = (curr_datetime - timedelta(days=3)).isoformat(),endtime = (curr_datetime-timedelta(days=1)).isoformat(), symbol = 'AAPL'):
        #get data from Alpaca API

        DATA = api.get_bars(symbol = symbol, timeframe = '5Min',start = starttime, end = endtime)
        DATA = DATA.df
        DATA[symbol] = DATA.open
        return pd.DataFrame(DATA[symbol])
    




