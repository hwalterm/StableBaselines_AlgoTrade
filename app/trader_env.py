#
# Created on Wed Aug 10 2022
#
# Copyright (c) 2022 H. Alterman
#

from math import inf
import gym
import numpy as np
import pandas as pd
#print('testtest')

import marketsimcode

#########################################################################################
#the below environment expects:
# 1. a price df with the bar close prices in the closing column and the times in the index
# 2. an indicator df with each unbounded indicator in its own column and an index that matches the price df index
# the indicator df should additionally included a 'position' column that is initialized to 0
# and updated at each step
##########################################################################################
class StockTradeEnv(gym.Env):
    def __init__(self,
        observation_shape =(2,), 
        action_space =3, 
        marketsimulator:marketsimcode.marketsim = None,
        price_df: pd.DataFrame = pd.DataFrame(data={'AAPL':[0]}),
        indicator_df: pd.DataFrame = pd.DataFrame(data={'position':[0],'indicator1':[0]}),
        symbol = 'AAPL',
        max_trade = 60,transaction_cost_percent = .000001):
        self.symbol =symbol
        self.position = {'position':0,'price':0}
        self.price_df = price_df
        self.indicator_df = indicator_df
        self.current_index = 0 
        self.max_trade = max_trade
        self.observation_shape = observation_shape
        self.action_space = gym.spaces.Discrete(action_space)
        self.observation_space = gym.spaces.Box(low = -inf, high = inf,shape = observation_shape,
                                            dtype = float)
        self.marketsimulator = marketsimulator
        self.state = indicator_df.iloc[0,:]
        self.transaction_cost_percent = transaction_cost_percent

    def step(self, action):
        number_of_observations = len(self.price_df.index)
        last_index = number_of_observations -1
        
        
        
        #get the current price and current time
        #print('step {} taking action {}, position {}, target position {}'.format(self.current_index, order,self.position['position'],target_position))
        current_datetime = self.price_df.index[self.current_index]
        current_price = self.price_df.loc[current_datetime,self.symbol]
        
        #if it is the end of the data we will set our target position to zero. otherwise we will check our action
        if self.current_index+1 >= last_index:
            target_position = 0
        else:
            #if it is not the end of the data, but is the end of the day, also set to 0
            next_datetime = self.price_df.index[self.current_index +1]
            if current_datetime.date() < next_datetime.date():
                target_position = 0
            else:
                #otherwise we will use learner action
                #action is an int between 0 and action space -1 ([0,2]) so we subtract 1 so it will be -1,0 or 1
                #depending on whether we should have a short position, no position or long position
                target_position = (action-1) * self.max_trade

        #amount to order will be the target position minus current position
        order = target_position - self.position['position']

        #if we are closing a short position or a long position calculate the reward
        #closing a position means either we own negative shares and are buying, or own positive shares and are sellign
  
        if (abs(target_position - self.position['position'])>.001):
            #reward will be equal to the new (price - old price) * shares that were traded
            #if we are closing a short position order will be positive. reward will be positive if price < old price
            #if we are closing a long position order will be negative. reward will be positive if price > old price
            #print('current price {}, position price {} '.format(current_price, self.position['price']))
            reward = (current_price - self.position['price']) * float(self.position['position']) *1.0
            if self.position['position'] == 0:
                reward = 0
            self.position['position'] = target_position
            self.position['price'] = current_price

            
            
        
        else:
            reward = 0
        
        transaction_cost = abs(order) * abs(current_price) * abs(self.transaction_cost_percent)
        reward = reward - transaction_cost

        # print('step {} taking action {}, position {}, target position {}'.format(self.current_index, order,self.position['position'],target_position))
        # print('current datetime {}'.format(current_datetime))
        
        
        #if we have another observation go to next, otherwise go to first observation
        if self.current_index<number_of_observations-1:
            #print('current_index {} number of observation {}'.format(self.current_index, number_of_observations))
            self.current_index = self.current_index + 1 
        else:
            self.current_index = 0
        current_datetime = self.price_df.index[self.current_index]

        
        #print('current_index {} number of observation {}'.format(self.current_index, number_of_observations))
        
        #update the current state to reflect our new position
        self.indicator_df.loc[current_datetime,'position'] = float(order)
        #print('next position: {}'.format(self.indicator_df.loc[current_datetime,'position']))
        state = self.indicator_df.loc[current_datetime].to_numpy()
        done = False
        info = {}
        #print('reward: {}'.format(reward))
        return state, reward, done, info
    
    def reset(self):
        print('resetting')
        self.indicator_df['position'] = 0
        self.current_index = 0
        current_datetime = self.price_df.index[self.current_index]
        state = self.indicator_df.loc[current_datetime]
        print('observation shape {} current state shape {}'.format(self.observation_shape,state.to_numpy().shape))
        # print(state.to_numpy())
     
        return state.to_numpy()
    


#trader_env = StockTradeEnv(observation_shape=(5,))