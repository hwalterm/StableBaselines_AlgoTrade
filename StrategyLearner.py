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
        self.learner = QLearner(num_states = 1000, num_actions = 3)  	
        self.Marketsimulator = marketsimulator	  	  			  		 			     			  			     			  	 


    def compute_reward(self, holdings, start_cash =10000):
        #print('compute reward')
        df = pd.DataFrame(holdings)
        df['previous_position'] = df['position'].shift()
        df['previous_position'] = df['previous_position'].fillna(0)
        df['orders'] = df['position'] - df['previous_position']
        portval = self.Marketsimulator.compute_portvals(orders_df = df['orders'], start_val=start_cash)
        profit = portval[-1]  - start_cash
        return profit		  	  			  		 			     			  	 
  		  	   		  

      		  	   		  	  			  		 			     			  	 
    # this method should create a QLearner, and train it for trading  		  	   		  	  			  		 			     			  	 
    def add_evidence(  		  	   		  	  			  		 			     			  	 
        self,  		  	   		  	  			  		 			     			  	 
        symbol="IBM",  		  	   		  	  			  		 			     			  	 
        sd=dt.datetime(2008, 1, 1),  		  	   		  	  			  		 			     			  	 
        ed=dt.datetime(2009, 1, 1),  		  	   		  	  			  		 			     			  	 
        sv=100000,  		  	   		  	  			  		 			     			  	 
    ):  
        syms = [symbol]  		  	   		  	  			  		 			     			  	 
        dates = pd.date_range(sd, ed)  		  	   		  	  			  		 			     			  	 
        prices_all = self.Marketsimulator.PRICES 	  	   		  	  			  		 			     			  	 
        prices = prices_all[syms]  # only portfolio symbols  		  	   		  	  			  		 			     			  	 
       	  	   		  	  			  		 			     			  	 
        # if self.verbose:  		  	   		  	  			  		 			     			  	 
        #     print(prices) 
        df = pd.DataFrame()
        df['price'] = prices_all[symbol]
        df['next_price'] = prices_all[symbol].shift(-1)
        df['daily_return_ontrade'] = (df['next_price'] - df['price'])/df['price']
        df['sma'] = indicators.run_SMA(prices,symbol=symbol)
        df['momentum'] = -indicators.run_momentum(prices,symbol=symbol)
        df['stochasticos'] = indicators.run_stochasticos(prices,symbol=symbol)
        df['bollinger'] = indicators.run_bollinger(prices,symbol=symbol)	

        df.fillna(method = 'bfill', inplace=True)
        df.fillna(method = 'ffill', inplace =True)

        discretize_indicators_sma = pd.cut(df['sma'],bins = 10,labels=False, retbins=True,)[0]
        discretize_indicators_sma = discretize_indicators_sma.astype(str)
        

        discretize_indicators_stoc = pd.cut(df['stochasticos'],bins = 10,labels=False, retbins=True,)[0]
        discretize_indicators_stoc = discretize_indicators_stoc.astype(str)

        discretize_indicators_bol = pd.cut(df['bollinger'],bins = 10,labels=False, retbins=True,)[0]
        discretize_indicators_bol = discretize_indicators_sma.astype(str) 


        #discrete_indicators = discretize_indicators_sma + (discretize_indicators_stoc) + (discretize_indicators_bol)
        
        discrete_indicators = discretize_indicators_sma + discretize_indicators_stoc + discretize_indicators_bol
        discrete_indicators = discrete_indicators.astype(int)
        df['discrete_indicator'] = discrete_indicators
        #print(discrete_indicators)
        #set initial state
        self.a = self.learner.querysetstate(discrete_indicators[0])
        df['position'] = 0
  

        shares_to_trade = 60
        
        r= 0
        previous_r = -99999
        action_dict = {0:-shares_to_trade
                        ,1: shares_to_trade
                        ,2:0}
        t_end = time.time() +30

        while (time.time()< t_end):
            previous_r = r
        
            for index,value in discrete_indicators.iteritems():
            
                action = self.learner.query(s_prime = value,r =r )
         
                position = action_dict[action]
                df['position'][index] = position
                r = self.compute_reward(holdings=df['position'])
                print(r)
                #transaction costs
                impact_amount = (df['next_price'][index] * position) * self.impact
                r = r - (self.commission + abs(impact_amount))



    
          

                



   		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
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
   
        prices = self.Marketsimulator.PRICES


        df = pd.DataFrame()
        df['sma'] = indicators.run_SMA(prices,symbol=symbol)
        df['momentum'] = -indicators.run_momentum(prices,symbol=symbol)
        df['stochasticos'] = indicators.run_stochasticos(prices,symbol=symbol)
        df['bollinger'] = indicators.run_stochasticos(prices,symbol=symbol)
        # print(df.head(20))
        df.fillna(method = 'bfill', inplace=True)
        df.fillna(method = 'ffill', inplace =True)

        discretize_indicators_sma = pd.cut(df['sma'],bins = 10,labels=False, retbins=True,)[0]
        discretize_indicators_sma = discretize_indicators_sma.astype(str)
        

        discretize_indicators_stoc = pd.cut(df['stochasticos'],bins = 10,labels=False, retbins=True,)[0]
        discretize_indicators_stoc = discretize_indicators_stoc.astype(str)

        discretize_indicators_bol = pd.cut(df['bollinger'],bins = 10,labels=False, retbins=True,)[0]
        discretize_indicators_bol = discretize_indicators_sma.astype(str) 

        #discrete_indicators = discretize_indicators_sma + (discretize_indicators_stoc) + (discretize_indicators_bol)
        
        discrete_indicators = discretize_indicators_sma + discretize_indicators_stoc + discretize_indicators_bol
        discrete_indicators = discrete_indicators.astype(int)
        start = time.process_time()

        shares_to_trade = 60
        action_dict = {0:-shares_to_trade
                        ,1: shares_to_trade
                        ,2:0}
        df['position'] = 0
        df['position'] = discrete_indicators.apply(self.learner.querysetstate)
        df['position'] = df['position'].map(action_dict)
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
