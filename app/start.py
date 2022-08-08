import alpaca_trade_api as tradeapi
import StrategyLearner as sl
from marketsimcode import marketsim
from datetime import datetime,timezone, timedelta
import pandas as pd
import live_trader
import threading
import time
import logging
import sys
logging.basicConfig(filename='app_logs.log',
         format='%(asctime)s %(message)s', 
         level=logging.INFO, filemode = 'w')
# API Info for fetching data, portfolio, etc. from Alpaca
print('start')
pd.set_option('display.max_rows', 100)
BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_API_KEY = "PKY5G9B86FNQEYQARRFK"
ALPACA_SECRET_KEY = "kYcBaE4p2H1Itcwnr9VIxN3ixNyd5Jizd3kVtOfR"
curr_datetime = datetime.now(timezone.utc)
api = tradeapi.REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, 
                    base_url=BASE_URL, api_version='v2')
def get_and_clean_data(starttime = (curr_datetime - timedelta(days=3)).isoformat(),endtime = (curr_datetime-timedelta(days=1)).isoformat(), symbol = 'AAPL'):
    #get data from Alpaca API
    
    DATA = api.get_bars(symbol = symbol, timeframe = tradeapi.TimeFrame.Minute,start = starttime, end = endtime)
    DATA = DATA.df
    DATA[symbol] = DATA.close
    return pd.DataFrame(DATA[symbol])
def get_SPY_data (starttime = (curr_datetime - timedelta(days=3)).isoformat(),
                    endtime = (curr_datetime-timedelta(days=1)).isoformat()):

    DATA = api.get_bars(symbol = "SPY", timeframe = '1Min',start = starttime, end = endtime)
    #print(DATA.df)
    DATA = DATA.df
    DATA["SPY"] = DATA.close
    return DATA["SPY"]



def train_test_strategy_learner(symbol = "AAPL",
    training_sd=(curr_datetime - timedelta(days=6)).isoformat(),
    training_ed=(curr_datetime-timedelta(days=5)).isoformat(),
    testing_sd =(curr_datetime - timedelta(days=5)).isoformat(),
    testing_ed =(curr_datetime - timedelta(days = 4)).isoformat()

     ):
    ##################################################################################
    #Create a Q learner strategy based on historic data
    ##################################################################################
    #Get market data
    data = get_and_clean_data(starttime=training_sd,
                            endtime = training_ed,
                            symbol = symbol
                            )
    SPY = get_SPY_data(
                            starttime=training_sd,
                            endtime = training_ed,
    )
    #create marketsimulator
    marketsimulator = marketsim(PRICES = data, symbols = [symbol],SPY = SPY)
    #Create and train learner
    learner = sl.StrategyLearner(verbose = True, impact = 0.0, commission=0.0,marketsimulator=marketsimulator) # constructor 
    learner.add_evidence(symbol = symbol, sd=datetime(2008,1,1), ed=datetime(2009,12,31), sv = 100000) # training phase 

    #update marketsim to use testing data
    data = get_and_clean_data(starttime=testing_sd,
                            endtime = testing_ed,
                            )
    SPY = get_SPY_data(
                            starttime=testing_sd,
                            endtime = testing_ed,
    )
    marketsimulator = marketsim(PRICES = data, symbols = [symbol],SPY = SPY)
    learner.Marketsimulator = marketsimulator
    orders = learner.testPolicy(symbol = symbol) # testing phase 

    
    portval = marketsimulator.compute_portvals( orders_df = orders['orders'], 
                    start_val=100000, debug = True)
    show_df = pd.DataFrame()
    show_df['orders']= orders
    show_df['portval'] = portval
    show_df[symbol] = marketsimulator.PRICES[symbol]
    print(show_df.tail(100))
    return portval, learner
def awaitMarketOpen():
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
    print("Waiting for market to open...")
    tAMO = threading.Thread(target=awaitMarketOpen)
    tAMO.start()
    tAMO.join()
    print("Market opened")
    
def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate
if __name__ == '__main__':
    symbol = 'AAPL'
    if len(sys.argv)>1:
        symbol = sys.argv[1]


    # training_sd=(curr_datetime- timedelta(days=4)).isoformat()
    # training_ed = (curr_datetime- timedelta(days=3)).isoformat(),
    # testing_sd =(curr_datetime- timedelta(days=1)).isoformat(),
    # testing_ed = (curr_datetime- timedelta(minutes =15)).isoformat(),

    training_sd=prev_weekday(curr_datetime).isoformat()
    training_ed = (curr_datetime- timedelta(minutes=15)).isoformat()
    testing_sd =prev_weekday(curr_datetime).isoformat()
    testing_ed = (curr_datetime- timedelta(minutes=15)).isoformat()
    #run_awaitMarketOpen()
    print('train learner')
    testval, learner = train_test_strategy_learner(symbol=symbol,
                                                training_sd=training_sd,
                                                training_ed=training_ed,
                                                testing_sd=testing_sd,
                                                testing_ed=testing_ed
                                                )
    
    print('wait 8 minutes for non nan indicators')
    time.sleep(480)
    print('running_live')
    
    trader = live_trader.live_trader(learner=learner,
    Qlearner = learner.learner, symbol = symbol)
    trader.consumer_thread()
    print('after consumer thread')



# Fetch Apple data from last 100 days
#APPLE_DATA = api.get_bars(symbol = 'AAPL', timeframe = '5Min',start = starttime, end = endtime)
