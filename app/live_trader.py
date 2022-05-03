import alpaca_trade_api as tradeapi
import StrategyLearner as sl
from marketsimcode import marketsim
from datetime import datetime,timezone, timedelta
import pandas as pd
import logging
import time
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
# API Info for fetching data, portfolio, etc. from Alpaca
print('beginning live trade')
BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_API_KEY = "PKVH1SZ416UXYP2WMQDC"
ALPACA_SECRET_KEY = "RSuMJdSnBkHBpSxpWOiipyjTWOsqwgiPmBJYse3j"
curr_datetime = datetime.now(timezone.utc)

class live_trader(object):
    def __init__(self,
                learner,
                symbol = 'AAPL', 
                order_size = 100,               
                ttc = 99):
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
        self.count_of_prices_to_retain = 40
   

    def consumer_thread(self):

        conn = Stream(ALPACA_API_KEY,
                    ALPACA_SECRET_KEY,
                    base_url=URL('https://paper-api.alpaca.markets'),
                    data_feed='iex')
        
        async def handle_bar(bar):
            print(bar.close)
            #if there are less than 20 bars, add the bar otherwise keep only the last 19 and add the newest
            if (len(self.close_prices)< self.count_of_prices_to_retain):
                self.close_prices.append(bar.close)
            else:
                self.close_prices = (self.close_prices[-19:]).append(bar.close)
                self.execute_QAction()

            print(self.close_prices)
            
            #update bars to add new list
            print('bar', bar)

        async def handle_SPY(bar):
            if (len(self.SPY_prices)< self.count_of_prices_to_retain):
                self.SPY_prices.append(bar.close)
            else:
                self.SPY_prices = (self.close_prices[-19:]).append(bar.close)

   
        conn.subscribe_bars(handle_SPY,'SPY')
        conn.subscribe_bars(handle_bar, self.symbol)
        conn.run()

    def execute_QAction(self):

        #Get the difference between current and target position
        print('get_Qaction prices: '.format(self.close_prices))
        print(self.close_prices)
        current_position = 0
        try:
            current_position = int(self.api.get_position(symbol = self.symbol).qty)
        except tradeapi.rest.APIError:
            current_position = 0
        #query the learner to get the prices
        target_position = self.learner.query_for_live_data(prices = self.close_prices,
                                                 spy_prices = self.SPY_prices,
                                                 order_size = self.order_size,
                                                 symbol = self.symbol
                                                 )
        difference_between_target = abs(target_position - current_position)
        #if we are not at our position cancel existing trades and make a trade to achieve desired position
        if difference_between_target != 0:
            #create a new order
            order_type = "sell" if difference_between_target < 0 else 'buy'
            self.api.submit_order(
                symbol=self.symbol,
                qty=difference_between_target,
                side=order_type,
                type='limit',
                time_in_force='ioc',
                limit_price=self.close_prices[-1]
            )


    def get_and_clean_data(starttime = (curr_datetime - timedelta(days=3)).isoformat(),endtime = (curr_datetime-timedelta(days=1)).isoformat(), symbol = 'AAPL'):
        #get data from Alpaca API

        DATA = api.get_bars(symbol = symbol, timeframe = '5Min',start = starttime, end = endtime)
        DATA = DATA.df
        DATA[symbol] = DATA.open
        return pd.DataFrame(DATA[symbol])



