""""""  		  	   		  	  			  		 			     			  	 
"""MC2-P1: Market simulator.  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
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
import os  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
import numpy as np  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
import pandas as pd  		  	   		  	  			  		 			     			  	 
#from util import get_data, plot_data  		  	   		  	  			  		 			     			  	 
class marketsim(object):	  	   		  	  			  		 			     			  	 
    def __init__(self, PRICES,symbols):
        self.PRICES = PRICES
        self.symbols = symbols

    def compute_portvals( 		  	   		  	  			  		 			     			  	 
        self,
        orders_df,  		  	   		  	  			  		 			     			  	 
        start_val=100000,	  	   		  	  			  		 			     			  	 
        commission=9.95,  		  	   		  	  			  		 			     			  	 
        impact=0.005,  		  	   		  	  			  		 			     			  	 
    ):  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        Computes the portfolio values.  		  	   		  	  			  		 			     			  	 
                                                                                
        :param orders_file: Path of the order file or the file object  		  	   		  	  			  		 			     			  	 
        :type orders_file: str or file object  		  	   		  	  			  		 			     			  	 
        :param start_val: The starting value of the portfolio  		  	   		  	  			  		 			     			  	 
        :type start_val: int  		  	   		  	  			  		 			     			  	 
        :param commission: The fixed amount in dollars charged for each transaction (both entry and exit)  		  	   		  	  			  		 			     			  	 
        :type commission: float  		  	   		  	  			  		 			     			  	 
        :param impact: The amount the price moves against the trader compared to the historical data at each transaction  		  	   		  	  			  		 			     			  	 
        :type impact: float  		  	   		  	  			  		 			     			  	 
        :return: the result (portvals) as a single-column dataframe, containing the value of the portfolio for each trading day in the first column from start_date to end_date, inclusive.  		  	   		  	  			  		 			     			  	 
        :rtype: pandas.DataFrame  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        # this is the function the autograder will call to test your code  		  	   		  	  			  		 			     			  	 
        # NOTE: orders_file may be a string, or it may be a file object. Your  		  	   		  	  			  		 			     			  	 
        # code should work correctly with either input  		  	   		  	  			  		 			     			  	 
        # TODO: Your code here  		  	   		  	  			  		 			     			  	 
                                                                                
        # In the template, instead of computing the value of the portfolio, we just  		  	   		  	  			  		 			     			  	 
        # read in the value of IBM over 6 months  		  	   		  	  			  		 			     			  	 
        orders = orders_df

        
        symbols = self.symbols


        symbol = self.symbols[0]
   
    
    
        prices = self.PRICES
        #prices.drop('SPY', axis = 'columns', inplace = True)
        prices['cash'] = 1

        #initialize trades df
        TRADES_DF = prices.copy()
        TRADES_DF['cash_change']=0
        #initialize holdings df
        HOLDINGS_DF = prices.copy()
        HOLDINGS_DF['cash'] = start_val
        #HOLDINGS_DF.loc[first_day,'cash'] = 
        
    
        

        #add columns for trades populate with zeroes. 
        #replace holdings df with zeros
        for s in symbols:
            TRADES_DF[s+'_orders'] = 0
            HOLDINGS_DF[s]=0
        #add order data to trades df
        TRADES_DF['cash_change']=0
        # for i,row in orders.iterrows():
        #     trade_date = row['Date']
        #     symbol = row['Symbol']
        #     shares = row['Shares'] if (row['Order'].upper() == 'BUY') else -row['Shares']
        #     order_amount = shares * prices[symbol][trade_date]
        #     #################################
        #     # Transaction Cost
        #     #################################
        #     #commission
        #     TRADES_DF.loc[trade_date,'cash_change'] -= commission
        #     #impact
        #     impact_val = abs(impact*order_amount)
        #     TRADES_DF.loc[trade_date,'cash_change'] -= impact_val



        #     #################################
        #     # Transaction Cost
        #     #################################
        impact_prices = prices[symbol] * impact

        transactioncosts = np.where(abs(orders) >0, impact_prices + commission, 0)
        #cash change
        cash_change = (orders * -prices[symbol]) + transactioncosts
        TRADES_DF['cash_change'] = cash_change
  
        
        #populate Holdings df
        for s in symbols:
            TRADES_DF[s+'_orders'] = orders
            HOLDINGS_DF[s] = TRADES_DF[s+'_orders'].cumsum()
        
        TRADES_DF['cash'] = TRADES_DF['cash_change'].cumsum()

        #print(TRADES_DF)
        HOLDINGS_DF['cash'] = HOLDINGS_DF['cash'] + TRADES_DF['cash']
        #print(HOLDINGS_DF)
        
        # print('TRADES_DF: {}'.format(TRADES_DF[['SPY_orders','GOOG_orders','XOM_orders','IBM_orders',
        # 'AAPL_orders','cash']]))
        # print('TRADES_DF: {}'.format(TRADES_DF))
        # print('HOLDINGS_DF: {}'.format(HOLDINGS_DF))
        #calculate values
        # print('prices keys: {}'.format(prices.keys()))
        # print('holdings keys: {}'.format(HOLDINGS_DF.keys()))
        #print(prices)
        VALUES_DF = self.PRICES * HOLDINGS_DF
        #print('VALUES_DF: {}'.format(VALUES_DF))
        
        portvals = VALUES_DF.sum(axis = 1)
        #print(portvals)

    
                                                                                                                                                    
        return portvals  		  	   		  	  			  		 			     			  	 
                                                                                
                                                                                
#     def test_code():  		  	   		  	  			  		 			     			  	 
#         """  		  	   		  	  			  		 			     			  	 
#         Helper function to test code  		  	   		  	  			  		 			     			  	 
#         """  		  	   		  	  			  		 			     			  	 
#         # this is a helper function you can use to test your code  		  	   		  	  			  		 			     			  	 
#         # note that during autograding his function will not be called.  		  	   		  	  			  		 			     			  	 
#         # Define input parameters  		  	   		  	  			  		 			     			  	 
                                                                                
#         of = "./orders/orders-02.csv"  		  	   		  	  			  		 			     			  	 
#         sv = 1000000  		  	   		  	  			  		 			     			  	 
                                                                                
#         # Process orders  		  	   		  	  			  		 			     			  	 
#         portvals = self.compute_portvals(orders_file=of, start_val=sv,commission=9.95, impact =.005) 
#         #print(portvals) 		  	   		  	  			  		 			     			  	 
#         if isinstance(portvals, pd.DataFrame):  		  	   		  	  			  		 			     			  	 
#             portvals = portvals[portvals.columns[0]]  # just get the first column  		  	   		  	  			  		 			     			  	 
#         else:  		  	   		  	  			  		 			     			  	 
#             "warning, code did not return a DataFrame"  		  	   		  	  			  		 			     			  	 
                                                                                
#         # Get portfolio stats  		  	   		  	  			  		 			     			  	 
#         # Here we just fake the data. you should use your code from previous assignments.  		  	   		  	  			  		 			     			  	 
#         start_date = dt.datetime(2008, 1, 1)  		  	   		  	  			  		 			     			  	 
#         end_date = dt.datetime(2008, 6, 1)  		  	   		  	  			  		 			     			  	 
#         cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [  		  	   		  	  			  		 			     			  	 
#             0.2,  		  	   		  	  			  		 			     			  	 
#             0.01,  		  	   		  	  			  		 			     			  	 
#             0.02,  		  	   		  	  			  		 			     			  	 
#             1.5,  		  	   		  	  			  		 			     			  	 
#         ]  		  	   		  	  			  		 			     			  	 
#         cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [  		  	   		  	  			  		 			     			  	 
#             0.2,  		  	   		  	  			  		 			     			  	 
#             0.01,  		  	   		  	  			  		 			     			  	 
#             0.02,  		  	   		  	  			  		 			     			  	 
#             1.5,  		  	   		  	  			  		 			     			  	 
#         ]  		  	   		  	  			  		 			     			  	 
                                                                                
  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
# if __name__ == "__main__":  		  	   		  	  			  		 			     			  	 
#     test_code()  		  	   		  	  			  		 			     			  	 
