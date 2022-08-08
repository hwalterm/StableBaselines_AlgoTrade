from math import inf
import gym
import numpy as np
import pandas as pd
print('testtest')

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
        max_trade = 60):
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

    def step(self, action):
        number_of_observations = len(self.price_df.index)
        


        

        #action is an int between 0 and action space -1 ([0,2]) so we subtract 1 so it will be -1,0 or 1
        #depending on whether we should have a short position, no position or long position
        target_position = (action-1) * self.max_trade
        #amount to order will be the target position minus current position
        order = target_position - self.position['position']
        #get the current price and current time
        print('step {} taking action {}, position {}, target position {}'.format(self.current_index, order,self.position['position'],target_position))
        current_datetime = self.price_df.index[self.current_index]
        current_price = self.price_df.loc[current_datetime,self.symbol]
        #print('current position: {}'.format(self.indicator_df.loc[current_datetime,'position']))

        #if we are closing a short position or a long position calculate the reward
        #closing a position means either we own negative shares and are buying, or own positive shares and are sellign
  
        if (abs(target_position - self.position['position'])>.001):
            #reward will be equal to the new (price - old price) * shares that were traded
            #if we are closing a short position order will be positive. reward will be positive if price < old price
            #if we are closing a long position order will be negative. reward will be positive if price > old price
            print('current price {}, position price {} '.format(current_price, self.position['price']))
            reward = (current_price - self.position['price']) * float(self.position['position']) *1.0
            if self.position['position'] == 0:
                reward = 0
            self.position['position'] = target_position
            self.position['price'] = current_price

            
            
        
        else:
            reward = 0
        
        print('reward: {}'.format(reward))
        #if we have another observation go to next, otherwise go to first observation
        if self.current_index<number_of_observations-1:
            #print('current_index {} number of observation {}'.format(self.current_index, number_of_observations))
            self.current_index = self.current_index + 1 
        else:
            self.current_index = 0
        current_datetime = self.price_df.index[self.current_index]
        #print('current_index {} number of observation {}'.format(self.current_index, number_of_observations))
        #print('current datetime {}'.format(current_datetime))
        #update the current state to reflect our new position
        self.indicator_df.loc[current_datetime,'position'] = float(order)
        #print('next position: {}'.format(self.indicator_df.loc[current_datetime,'position']))
        state = self.indicator_df.loc[current_datetime].to_numpy()
        done = False
        info = {}
        #print('observation shape {} current state {}'.format(self.observation_shape,state))
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
    
    # def __setattr__(self, __name: str, __value: Any) -> None:
    #     return super().__setattr__(__name, __value)


#trader_env = StockTradeEnv(observation_shape=(5,))