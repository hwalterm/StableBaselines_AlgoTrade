""""""  		  	   		  	  			  		 			     			  	 
"""  		  	   		  	  			  		 			     			  	 
Template for implementing StrategyLearner  (c) 2016 Tucker Balch  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
Copyright 2018, Georgia Institute of Technology (Georgia Tech)  		  	   		  	  			  		 			     			  	 
Atlanta, Georgia 30332  		  	   		  	  			  		 			     			  	 
All Rights Reserved  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
Template code for CS 4646/7646  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
Georgia Tech asserts copyright ownership of this template and all derivative  		  	   		  	  			  		 			     			  	 
works, including solutions to the projects assigned in this course. Students  		  	   		  	  			  		 			     			  	 
and other users of this template code are advised not to share it with others  		  	   		  	  			  		 			     			  	 
or to make it available on publicly viewable websites including repositories  		  	   		  	  			  		 			     			  	 
such as github and gitlab.  This copyright statement should not be removed  		  	   		  	  			  		 			     			  	 
or edited.  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
We do grant permission to share solutions privately with non-students such  		  	   		  	  			  		 			     			  	 
as potential employers. However, sharing with other current or future  		  	   		  	  			  		 			     			  	 
students of CS 7646 is prohibited and subject to being investigated as a  		  	   		  	  			  		 			     			  	 
GT honor code violation.  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
-----do not edit anything above this line---  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
Student Name: Hershel Alterman 	  	   		  	  			  		 			     			  	 
GT User ID: halterman3 	  	   		  	  			  		 			     			  	 
GT ID: 903548572  		  	   		  	  			  		 			     			  	 
"""  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
import datetime as dt
import dis  		  	   		  	  			  		 			     			  	 
import random  as rand
from marketsimcode import marketsim	  	   		  	  			  		 			     			  	 
import numpy as np 		  	   		  	  			  		 			     			  	 
import pandas as pd		  	   		  	  			  		 			     			  	 
import indicators	  	   
import math
from QLearner import QLearner
import time	  




def author(self): 
    return 'halterman3' # replace tb34 with your Georgia Tech username.  	  		  	   		  	  			  		 			     			  	 
pd.options.mode.chained_assignment = None  		  	   		  	  			  		 			     			  	 
class StrategyLearner(object):  		  	   		  	  			  		 			     			  	 
    """  		  	   		  	  			  		 			     			  	 
    A strategy learner that can learn a trading policy using the same indicators used in ManualStrategy.  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
    :param verbose: If “verbose” is True, your code can print out information for debugging.  		  	   		  	  			  		 			     			  	 
        If verbose = False your code should not generate ANY output.  		  	   		  	  			  		 			     			  	 
    :type verbose: bool  		  	   		  	  			  		 			     			  	 
    :param impact: The market impact of each transaction, defaults to 0.0  		  	   		  	  			  		 			     			  	 
    :type impact: float  		  	   		  	  			  		 			     			  	 
    :param commission: The commission amount charged, defaults to 0.0  		  	   		  	  			  		 			     			  	 
    :type commission: float  		  	   		  	  			  		 			     			  	 
    """  		  	   		  	  			  		 			     			  	 
    # constructor  		  	   		  	  			  		 			     			  	 
    def __init__(self,marketsimulator,  verbose=False, impact=0, commission=0.0):  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        Constructor method  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        self.verbose = verbose  		  	   		  	  			  		 			     			  	 
        self.impact = impact  		  	   		  	  			  		 			     			  	 
        self.commission = commission
        self.learner = QLearner(num_states = 10000, num_actions = 3)  	
        self.Marketsimulator = marketsimulator
        self.train_time = 60
        #not currently using saved bins
        self.SPY_BINS =[] 
        self.STOC_BINS = []
        self.BOL_BINS = [] 	  			  		 			     			  			     			  	 


    def compute_reward(self, holdings, start_cash =10000):
        #print('compute reward')
        df = pd.DataFrame(holdings)
        df['previous_position'] = df['position'].shift()
        df['previous_position'] = df['previous_position'].fillna(0)
        df['orders'] = df['position'] - df['previous_position']
        portval = self.Marketsimulator.compute_portvals(orders_df = df['orders'], start_val=start_cash)
        profit = portval[-1]  - start_cash
        return profit

    def calculate_discrete_state(self,symbol,prices_all,spy_prices,
                            spy_bins = 10,
                            sma_bins = 10,
                            bol_bins = 10,
                            stoc_bins = 10,):	 
        syms = [symbol]  		  	   		  	  			  		 			     			  	 	  	   		  	  			  		 			     			  	 
	  	   		  	  			  		 			     			  	 
        prices = prices_all[syms]  # only portfolio symbols   
        df = pd.DataFrame()
        df['price'] = prices_all[symbol]
        df['next_price'] = prices_all[symbol].shift(-1)
        df['daily_return_ontrade'] = (df['next_price'] - df['price'])/df['price']
        df['sma'] = indicators.run_SMA(prices,symbol=symbol)
        df['momentum'] = -indicators.run_momentum(prices,symbol=symbol)
        df['stochasticos'] = indicators.run_stochasticos(prices,symbol=symbol)
        df['bollinger'] = indicators.run_bollinger(prices,symbol=symbol)	
        df['SPY_Ratio'] = indicators.run_SPY_Ratio(prices,spy_price_series=spy_prices,symbol=symbol)

        df.fillna(method = 'ffill', inplace=True)
        df.fillna(method = 'bfill', inplace =True)
        
        discretize_indicators_SPY,SPY_bins = pd.cut(df['SPY_Ratio'],bins = 10,labels=False, retbins=True,)
        self.SPY_BINS = SPY_bins
        discretize_indicators_SPY = discretize_indicators_SPY.astype(str)
        
        discretize_indicators_sma,sma_bins = pd.cut(df['sma'],bins = 10,labels=False, retbins=True,)
        discretize_indicators_sma = discretize_indicators_sma.astype(str)
        

        discretize_indicators_stoc,stoc_bins = pd.cut(df['stochasticos'],bins = 10,labels=False, retbins=True,)
        self.STOC_BINS = stoc_bins
        discretize_indicators_stoc= discretize_indicators_stoc.astype(str)

        discretize_indicators_bol,bol_bins = pd.cut(df['bollinger'],bins = 10,labels=False, retbins=True,)
        self.BOL_BINS = bol_bins
        discretize_indicators_bol = discretize_indicators_sma.astype(str) 


        #discrete_indicators = discretize_indicators_sma + (discretize_indicators_stoc) + (discretize_indicators_bol)
        
        discrete_indicators = discretize_indicators_stoc + discretize_indicators_bol + discretize_indicators_SPY
        discrete_indicators = discrete_indicators.astype(float).astype(int)
        df['discrete_indicator'] = discrete_indicators
        return df	  			  		 			     			  	 
  		  	   		  

      		  	   		  	  			  		 			     			  	 
    # this method should create a QLearner, and train it for trading  		  	   		  	  			  		 			     			  	 
    def add_evidence(  		  	   		  	  			  		 			     			  	 
        self,  		  	   		  	  			  		 			     			  	 
        symbol="IBM",  		  	   		  	  			  		 			     			  	 
        sd=dt.datetime(2008, 1, 1),  		  	   		  	  			  		 			     			  	 
        ed=dt.datetime(2009, 1, 1),  		  	   		  	  			  		 			     			  	 
        sv=100000,  		  	   		  	  			  		 			     			  	 
    ):  
        prices_all = self.Marketsimulator.PRICES
        spy_prices = self.Marketsimulator.SPY_PRICES		  	   		  	  			  		 			     			  	 
        df = self.calculate_discrete_state(symbol,
                prices_all=prices_all,spy_prices=spy_prices)	
        discrete_indicators	= df['discrete_indicator']
        discrete_indicators.index.values.astype(float)
        first_index = discrete_indicators.first_valid_index()
        index_time_interval = discrete_indicators.first_valid_index()			  		 			     			  	 
        # if self.verbose:  		  	   		  	  			  		 			     			  	 
        #     print(prices) 
    
        #print(discrete_indicators)
        #set initial state
        self.a = self.learner.querysetstate(discrete_indicators[0])
        df['position'] = 0
  

        shares_to_trade = 60
        
        r= 0
        previous_r = -99999

        #As standard encoding for the Q learner, we use:
        # 0 to denote a short position
        # 1 to denote long position
        # 2 to denote no
        action_dict = {0:-shares_to_trade
                        ,1: shares_to_trade
                        ,2:0}
        reverse_action_dict = {-shares_to_trade:0,
                                shares_to_trade:1,
                                0:2
        }
        t_end = time.time() +self.train_time
        previous_index = None
        while (time.time()< t_end):
            previous_r = r
        
            for index,value in discrete_indicators.iteritems():
                if index >first_index:
        
                    previous_action = reverse_action_dict[df['position'][previous_index]]
                    state = int(str(value) + str(previous_action))
                else:
                    state = int(str(value) + str(2))
                action = self.learner.query(s_prime = state,r =r )
         
                position = action_dict[action]
                df['position'][index] = position
                r = self.compute_reward(holdings=df['position'])
                print(r)
                #transaction costs
                impact_amount = (df['next_price'][index] * position) * self.impact
                r = r - (self.commission + abs(impact_amount))
                previous_index = index
                



    
          

                


    def query_for_live_data(self,prices,spy_prices, order_size = 50,symbol = 'AAPL',
                                current_position = 2):
        shares_to_trade = order_size

        #As standard encoding for the Q learner, we use:
        # 0 to denote a short position
        # 1 to denote long position
        # 2 to denote no
        state = int(str(value) + str(previous_action))


        
        df =pd.DataFrame()
        df[symbol] = prices
        df['SPY'] = spy_prices

        df = self.calculate_discrete_state(symbol,prices,spy_prices = spy_prices)	
        discrete_indicators	= df['discrete_indicator']	 
        action_dict = {0:-shares_to_trade
                        ,1: shares_to_trade
                        ,2:0}
        state = int(str(discrete_indicators[-1]) + str(current_position))
        
        action = self.learner.querysetstate(s = state)
        position = action_dict[action]
        #df['position'] = discrete_indicators.apply(self.learner.querysetstate)
        #df['position'] = df['position'].map(action_dict)
        return position
   		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
    # this method should use the existing policy and test it against new data  		  	   		  	  			  		 			     			  	 
    def testPolicy(  		  	   		  	  			  		 			     			  	 
        self,  		  	   		  	  			  		 			     			  	 
        symbol="IBM",  		  	   		  	  			  		 			     			  	 		  	   		  	  			  		 			     			  	   	   		  	  			  		 			     			  	 
    ):  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        Tests your learner using data outside of the training data  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
        :param symbol: The stock symbol that you trained on on  		  	   		  	  			  		 			     			  	 
        :type symbol: str  		  	   		  	  			  		 			     			  	 
        :param sd: A datetime object that represents the start date, defaults to 1/1/2008  		  	   		  	  			  		 			     			  	 
        :type sd: datetime  		  	   		  	  			  		 			     			  	 
        :param ed: A datetime object that represents the end date, defaults to 1/1/2009  		  	   		  	  			  		 			     			  	 
        :type ed: datetime  		  	   		  	  			  		 			     			  	 
        :param sv: The starting value of the portfolio  		  	   		  	  			  		 			     			  	 
        :type sv: int  		  	   		  	  			  		 			     			  	 
        :return: A DataFrame with values representing trades for each day. Legal values are +1000.0 indicating  		  	   		  	  			  		 			     			  	 
            a BUY of 1000 shares, -1000.0 indicating a SELL of 1000 shares, and 0.0 indicating NOTHING.  		  	   		  	  			  		 			     			  	 
            Values of +2000 and -2000 for trades are also legal when switching from long to short or short to  		  	   		  	  			  		 			     			  	 
            long so long as net holdings are constrained to -1000, 0, and 1000.  		  	   		  	  			  		 			     			  	 
        :rtype: pandas.DataFrame  		  	   		  	  			  		 			     			  	 
        """  
        start = time.process_time()
        prices_all = self.Marketsimulator.PRICES
        spy_prices = self.Marketsimulator.SPY_PRICES		  	   		  	  			  		 			     			  	 
        df = self.calculate_discrete_state(symbol,
                prices_all=prices_all,spy_prices=spy_prices,
                spy_bins = self.SPY_BINS,
                stoc_bins = self.STOC_BINS,
                bol_bins =self.BOL_BINS 	  			  		 			     			  			     			  	 
)	
        discrete_indicators	= df['discrete_indicator']	 
        start = time.process_time()
        df['position'] = 0
        #discrete_indicators.index.values.astype(float)
        first_index = discrete_indicators.first_valid_index()
        shares_to_trade = 60
        action_dict = {0:-shares_to_trade
                        ,1: shares_to_trade
                        ,2:0}
        reverse_action_dict = {-shares_to_trade:0,
                                shares_to_trade:1,
                                0:2
        }
        previous_index=0
  
        for index,value in discrete_indicators.iteritems():
            if index >first_index:
                #print(str(df['position'][previous_index]))
                previous_action = reverse_action_dict[df['position'][previous_index]]
                state = int(str(value) + str(previous_action))
            else:
                state = int(str(value) + str(2))
                
            action = self.learner.querysetstate(s = state)
         
            position = action_dict[action]
            df['position'][index] = position
            previous_index = index

       
  
        # df['position'] = discrete_indicators.apply(self.learner.querysetstate)
        # df['position'] = df['position'].map(action_dict)
        # for index,value in discrete_indicators.iteritems():
            
        #     action = self.learner.querysetstate(s = value)
        #     position = action_dict[action]
        #     df['position'][index] = position
        df['previous_position'] = df['position'].shift()
        df['previous_position'][0] = 0
        df['orders'] = df['position'] - df['previous_position']

        #print(df['orders'].head(100))
        #df['orders'] = df['orders'].astype(int)

        return pd.DataFrame(df['orders'])
    def author(self): 
        return 'halterman3' # replace tb34 with your Georgia Tech username.  	




	  	 

        
        	  	   		  	  			  		 			     			  	 

 	  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
   


    		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
    def author(self):                                                                                              
        """                                                                                              
        :return: The GT username of the student                                                                                              
        :rtype: str                                                                                              
        """                                                                                              
        return "halterman3"   		  	   		  	  			  		 			     			  	 
if __name__ == "__main__":  		  	   		  	  			  		 			     			  	 
    print("One does not simply think up a strategy")  		  	   		  	  			  		 			     			  	 
