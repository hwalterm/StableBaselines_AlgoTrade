import alpaca_trade_api as tradeapi
import StrategyLearner as sl
from marketsimcode import marketsim
from datetime import datetime,timezone, timedelta
import pandas as pd
import live_trader
# API Info for fetching data, portfolio, etc. from Alpaca
print('start')
BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_API_KEY = "PKEYG0E4ONCK4THYJE7O"
ALPACA_SECRET_KEY = "cdgmSM2qnh9CNCUrmj5kkXeiKtaOVAQRcaRj2uUd"
curr_datetime = datetime.now(timezone.utc)
def get_and_clean_data(starttime = (curr_datetime - timedelta(days=3)).isoformat(),endtime = (curr_datetime-timedelta(days=1)).isoformat(), symbol = 'AAPL'):
    #get data from Alpaca API
    api = tradeapi.REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, 
                    base_url=BASE_URL, api_version='v2')
    DATA = api.get_bars(symbol = symbol, timeframe = '1Min',start = starttime, end = endtime)
    DATA = DATA.df
    DATA[symbol] = DATA.close
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
                            symbol = symbol
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

if __name__ == '__main__':
    trader = live_trader.live_trader()
    trader.consumer_thread()
    #train_test_strategy_learner()

#training period
# curr_datetime = datetime.now(timezone.utc)
# starttime = curr_datetime - timedelta(days=3)
# endtime = curr_datetime.isoformat()
# train_test_strategy_learner()
# Instantiate REST API Connection

# Fetch Apple data from last 100 days
#APPLE_DATA = api.get_bars(symbol = 'AAPL', timeframe = '5Min',start = starttime, end = endtime)
