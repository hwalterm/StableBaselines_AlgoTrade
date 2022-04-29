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
ALPACA_API_KEY = "PKEYG0E4ONCK4THYJE7O"
ALPACA_SECRET_KEY = "cdgmSM2qnh9CNCUrmj5kkXeiKtaOVAQRcaRj2uUd"
curr_datetime = datetime.now(timezone.utc)
api = tradeapi.REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, 
                    base_url=BASE_URL, api_version='v2')

class live_trader(object):
    def __init__(self):
        BASE_URL = "https://paper-api.alpaca.markets"
        ALPACA_API_KEY = "PKEYG0E4ONCK4THYJE7O"
        ALPACA_SECRET_KEY = "cdgmSM2qnh9CNCUrmj5kkXeiKtaOVAQRcaRj2uUd"
        curr_datetime = datetime.now(timezone.utc)
        api = tradeapi.REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, 
                            base_url=BASE_URL, api_version='v2')
        self.close_prices = []

    async def print_bar(bar):
        
        #update bars to add new list
        print('bar', bar)
    def consumer_thread(self):
        global conn
        conn = Stream(ALPACA_API_KEY,
                    ALPACA_SECRET_KEY,
                    base_url=URL('https://paper-api.alpaca.markets'),
                    data_feed='iex')

        conn.subscribe_bars(self.print_bar, 'AAPL')
        conn.run()


    def get_and_clean_data(starttime = (curr_datetime - timedelta(days=3)).isoformat(),endtime = (curr_datetime-timedelta(days=1)).isoformat(), symbol = 'AAPL'):
        #get data from Alpaca API

        DATA = api.get_bars(symbol = symbol, timeframe = '5Min',start = starttime, end = endtime)
        DATA = DATA.df
        DATA[symbol] = DATA.open
        return pd.DataFrame(DATA[symbol])

    def train_test_strategy_learner(symbol = "AAPL",
        training_sd=(curr_datetime - timedelta(days=3)).isoformat(),
        training_ed=(curr_datetime-timedelta(days=1)).isoformat(),
        testing_sd =(curr_datetime - timedelta(days=1)).isoformat(),
        testing_ed =(curr_datetime - timedelta(minutes = 30)).isoformat()

        ):
        ##################################################################################
        #Create a Q learner strategy based on historic data
        ##################################################################################
        #Get market data
        data = get_and_clean_data(starttime=training_sd,
                                endtime = training_ed,
                                )

        #create marketsimulator
        marketsimulator = marketsim(PRICES = data, symbols = [symbol])
        #Create and train learner
        learner = sl.StrategyLearner(verbose = True, impact = 0.0, commission=0.0,marketsimulator=marketsimulator) # constructor 
        learner.add_evidence(symbol = symbol, sd=datetime(2008,1,1), ed=datetime(2009,12,31), sv = 100000) # training phase 

        #update marketsim to use testing data
        data = get_and_clean_data(starttime=testing_sd,
                                endtime = testing_ed,
                                )
        marketsimulator = marketsim(PRICES = data, symbols = [symbol])
        learner.Marketsimulator = marketsimulator
        orders = learner.testPolicy(symbol = symbol) # testing phase 

        
        portval = marketsimulator.compute_portvals( orders_df = orders['orders'], start_val=100000)
        print(portval)
        return portval, learner

