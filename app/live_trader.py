import alpaca_trade_api as tradeapi
import StrategyLearner as sl
from QLearner import QLearner
from marketsimcode import marketsim
from datetime import datetime,timezone, timedelta
import pandas as pd
import logging
import time
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
import threading
import asyncio

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
                order_size = 100,               
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

        conn = Stream(ALPACA_API_KEY,
                    ALPACA_SECRET_KEY,
                    base_url=URL('https://paper-api.alpaca.markets'),
                    data_feed='iex')
        
        async def handle_bar(bar):
            print('bar', bar)
            #if there are less than 20 bars, add the bar otherwise keep only the last 19 and add the newest
            if (len(self.close_prices)< self.count_of_prices_to_retain):
                self.close_prices.append(bar.close)
            else:
                index_to_retain = self.count_of_prices_to_retain -1
                self.close_prices = (self.close_prices[-index_to_retain:])
                #######################################################
                #Get Q action
                # print('get_Qaction prices: '.format(self.close_prices))
                # print(self.close_prices)
                # current_position = 0
                # mapped_position = 2
                # try:
                #     current_position = int(self.api.get_position(symbol = self.symbol).qty)
                # except tradeapi.rest.APIError:
                #     print(tradeapi.rest.APIError)
                #     current_position = 0
                # print(current_position)
                #query the learner to get the prices
                # if current_position > 0 :
                #     mapped_position = 1
                # elif current_position < 0:
                #     mapped_position =0
                
                
                ####################################
                #query live data 
                # print('query for live data')
        
                # df =pd.DataFrame()
                
                # df[symbol] = prices
                # df['SPY'] = spy_prices
                # print(df)
                # print('prices: {}'.format(prices))
                # df = self.learner.calculate_discrete_state(symbol,prices_all = df,spy_prices = spy_prices)	
                # discrete_indicators	= df['discrete_indicator']
                # print('returned indicators {}'.format(discrete_indicators))	 
                # action_dict = {0:-shares_to_trade
                #                 ,1: shares_to_trade
                #                 ,2:0}
                # state = int(str(discrete_indicators[-1]) + str(current_position))
                # print('state: {}'.format(state))
                # action = self.Qlearner.querysetstate(s = state)
                # print('action: {}'.format(action))
                # position = action_dict[action]
                
                ####################################
    
            #update bars to add new list
            

        async def handle_SPY(bar):
            if (len(self.SPY_prices)< self.count_of_prices_to_retain):
                self.SPY_prices.append(bar.close)
            else:
                index_to_retain = self.count_of_prices_to_retain -1
                self.SPY_prices = self.SPY_prices[-index_to_retain:]
                self.SPY_prices.append(bar.close)

        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.run_forevs())
        print('set up bars')
        conn.subscribe_bars(handle_SPY,'SPY')
        conn.subscribe_bars(handle_bar, self.symbol)
        conn.run()
        print(self.timeToClose)

    async def run_forevs(self):
        while(1):
            print('running')
            time.sleep(10)
            print('still running')

    def execute_QAction(self):

        #Get the difference between current and target position
        print('get_Qaction prices: '.format(self.close_prices))
        print(self.close_prices)
        current_position = 0
        mapped_position = 2
        try:
            current_position = int(self.api.get_position(symbol = self.symbol).qty)
        except tradeapi.rest.APIError:
            print(tradeapi.rest.APIError)
            current_position = 0
        print(current_position)
        #query the learner to get the prices
        if current_position > 0 :
            mapped_position = 1
        elif current_position < 0:
            mapped_position =0

        target_position = self.query_for_live_data(prices = self.close_prices,
                                                 spy_prices = self.SPY_prices,
                                                 order_size = self.order_size,
                                                 symbol = self.symbol,
                                                 current_position = mapped_position
                                                 )
        
        print('target_position: {}'.format(target_position))
        difference_between_target = target_position - current_position
        transation_quantity = abs(difference_between_target)
        #if we are not at our position cancel existing trades and make a trade to achieve desired position
        if difference_between_target != 0:
            if self.is_EOD():
                self.close_all_positions_at_eod()
            else:
                print('submitting order for : {}'.format(difference_between_target))
            #create a new order
                order_type = "sell" if difference_between_target < 0 else 'buy'
                self.api.submit_order(
                    symbol=self.symbol,
                    qty=transation_quantity,
                    side=order_type,
                    type='limit',
                    time_in_force='ioc',
                    limit_price=self.close_prices[-1]
            )
    def is_EOD(self):
        minutes_before_close = 5
        clock = self.api.get_clock()
        closingTime = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
        currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
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




    def query_for_live_data(self,prices,spy_prices, order_size = 50,symbol = 'AAPL',
                                current_position = 2):
        shares_to_trade = order_size

        #As standard encoding for the Q learner, we use:
        # 0 to denote a short position
        # 1 to denote long position
        # 2 to denote no position

        print('query for live data')
        
        df =pd.DataFrame()
        
        df[symbol] = prices
        df['SPY'] = spy_prices
        print(df)
        print('prices: {}'.format(prices))
        df = self.learner.calculate_discrete_state(symbol,prices_all = df,spy_prices = spy_prices)	
        discrete_indicators	= df['discrete_indicator']
        print('returned indicators {}'.format(discrete_indicators))	 
        action_dict = {0:-shares_to_trade
                        ,1: shares_to_trade
                        ,2:0}
        print('curr pos:' + str(current_position))
        state = '999'
        print('state: {}'.format(state))
        action = 2
        #action = self.Qlearner.querysetstate(s = state)
        print('action: {}'.format(action))
        position = action_dict[action]
        return position        
    def get_and_clean_data(starttime = (curr_datetime - timedelta(days=3)).isoformat(),endtime = (curr_datetime-timedelta(days=1)).isoformat(), symbol = 'AAPL'):
        #get data from Alpaca API

        DATA = api.get_bars(symbol = symbol, timeframe = '5Min',start = starttime, end = endtime)
        DATA = DATA.df
        DATA[symbol] = DATA.open
        return pd.DataFrame(DATA[symbol])
    




