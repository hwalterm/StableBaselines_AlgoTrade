""""""  		  	   		  	  			  		 			     			  	 
"""  		  	   		  	  			  		 			     			  	 
Template for implementing QLearner  (c) 2015 Tucker Balch  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
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
  		  	   		  	  			  		 			     			  	 
Student Name: Hershel Alterman (replace with your name)  		  	   		  	  			  		 			     			  	 
GT User ID: halterman3(replace with your User ID)  		  	   		  	  			  		 			     			  	 
GT ID: 903548572 (replace with your GT ID)  		  	   		  	  			  		 			     			  	 
"""  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
import random as rand  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
import numpy as np
from NeuralNetwork import DQNLearner	  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
class QLearner(object):  		  	   		  	  			  		 			     			  	 
    """  		  	   		  	  			  		 			     			  	 
    This is a Q learner object.  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
    :param num_states: The number of states to consider.  		  	   		  	  			  		 			     			  	 
    :type num_states: int  		  	   		  	  			  		 			     			  	 
    :param num_actions: The number of actions available..  		  	   		  	  			  		 			     			  	 
    :type num_actions: int  		  	   		  	  			  		 			     			  	 
    :param alpha: The learning rate used in the update rule. Should range between 0.0 and 1.0 with 0.2 as a typical value.  		  	   		  	  			  		 			     			  	 
    :type alpha: float  		  	   		  	  			  		 			     			  	 
    :param gamma: The discount rate used in the update rule. Should range between 0.0 and 1.0 with 0.9 as a typical value.  		  	   		  	  			  		 			     			  	 
    :type gamma: float  		  	   		  	  			  		 			     			  	 
    :param rar: Random action rate: the probability of selecting a random action at each step. Should range between 0.0 (no random actions) to 1.0 (always random action) with 0.5 as a typical value.  		  	   		  	  			  		 			     			  	 
    :type rar: float  		  	   		  	  			  		 			     			  	 
    :param radr: Random action decay rate, after each update, rar = rar * radr. Ranges between 0.0 (immediate decay to 0) and 1.0 (no decay). Typically 0.99.  		  	   		  	  			  		 			     			  	 
    :type radr: float  		  	   		  	  			  		 			     			  	 
    :param dyna: The number of dyna updates for each regular update. When Dyna is used, 200 is a typical value.  		  	   		  	  			  		 			     			  	 
    :type dyna: int  		  	   		  	  			  		 			     			  	 
    :param verbose: If “verbose” is True, your code can print out information for debugging.  		  	   		  	  			  		 			     			  	 
    :type verbose: bool  		  	   		  	  			  		 			     			  	 
    """  		  	   		  	  			  		 			     			  	 
    def __init__(  		  	   		  	  			  		 			     			  	 
        self,  		  	   		  	  			  		 			     			  	 
        num_states=100,		  	   		  	  			  		 			     			  	 
        num_actions=3,  		  	   		  	  			  		 			     			  	 
        alpha=0.2,  		  	   		  	  			  		 			     			  	 
        gamma=0.9,  		  	   		  	  			  		 			     			  	 
        rar=0.5,  		  	   		  	  			  		 			     			  	 
        radr=0.9995,  		  	   		  	  			  		 			     			  	 
        dyna=0,  		  	   		  	  			  		 			     			  	 
        verbose=False,		  	   		  	  			  		 			     			  	 
    ):  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        Constructor method  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        self.verbose = verbose  		  	   		  	  			  		 			     			  	 
        self.num_actions = num_actions  		  	   		  	  			  		 			     			  	 
        self.s = np.zeros(4) 		  	   		  	  			  		 			     			  	 
        self.a = 0
        self.Q = [[0 for a in range(num_actions)] for s in range(num_states)]
        self.alpha =alpha
        self.gamma = gamma
        self.rar = rar
        self.dyna = dyna
        self.radr = radr
        self.T = {}
        self.NeuralNet = DQNLearner()
        self.num_indicators = 4
        # self.T = [[[0 for s_prime in range(num_states)] for a in range(num_actions)] for s in range(num_states)]
        # self.Tc = [[[0.00001 for s_prime in range(num_states)] for a in range(num_actions)] for s in range(num_states)]
          		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
    def querysetstate(self, s):  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        Update the state without updating the Q-table  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
        :param s: The new state  		  	   		  	  			  		 			     			  	 
        :type s: int  		  	   		  	  			  		 			     			  	 
        :return: The selected action  		  	   		  	  			  		 			     			  	 
        :rtype: int  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        self.s = s
        
        
        
        predictions = self.NeuralNet.predict(self.s)
        action = np.argmax(predictions[0])
        print('action: {}'.format(action))
        
        return action
        
        
        

          		  	   		  	  			  		 			     			  	 
        if self.verbose:  		  	   		  	  			  		 			     			  	 
            print(f"s = {s}, a = {action}")
        

        
        	  	   		  	  			  		 			     			  	 
        return action  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
    def query(self, s_prime, r):  		  	   		  	  			  		 			     			  	 
        """  		  	   		  	  			  		 			     			  	 
        Update the Q table and return an action  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
        :param s_prime: The new state  		  	   		  	  			  		 			     			  	 
        :type s_prime: int  		  	   		  	  			  		 			     			  	 
        :param r: The immediate reward  		  	   		  	  			  		 			     			  	 
        :type r: float  		  	   		  	  			  		 			     			  	 
        :return: The selected action  		  	   		  	  			  		 			     			  	 
        :rtype: int  		  	   		  	  			  		 			     			  	 
        """
        
        #self.NeuralNet.update(s_prime)
        #Determine Action
        #action = self.Q[s_prime].index(max(self.Q[s_prime]))
        New_NN_Prediction = self.NeuralNet.predict(s_prime)[0]

        #Qlearner predict 
        action = np.argmax(New_NN_Prediction)




        #update table with 
        #currentQ = self.Q[self.s][self.a]
        Current_NN_Prediction =self.NeuralNet.predict(self.s,)[0]
        currentQ = Current_NN_Prediction[self.a]
        
        #calculate the new q value for s and reward r
        laterQ = self.gamma * (max(New_NN_Prediction))
        #qprime = ((1-self.alpha )*(currentQ)) + (self.alpha * (r + laterQ))
        qprime = r + laterQ

        #update the neural network for state s reward r
        Current_NN_Prediction[self.a] = qprime
        self.NeuralNet.update(Current_NN_Prediction,state = self.s)
        #self.Q[self.s][self.a] =qprime
        print('current nn output: {}'.format(Current_NN_Prediction))
        

    

        		  	   		  	  			  		 			     			  	 
        
        if rand.random()  < self.rar:  
            action = rand.randint(0, self.num_actions - 1)
        self.rar = self.rar * self.radr 
        self.a = action
        self.s = s_prime
        		  	   		  	  			  		 			     			  	 
        return action 
    
    def author(self): 
        return 'halterman3' # replace tb34 with your Georgia Tech username.  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
  		  	   		  	  			  		 			     			  	 
if __name__ == "__main__":  		  	   		  	  			  		 			     			  	 
    print("Remember Q from Star Trek? Well, this isn't him")  		  	   		  	  			  		 			     			  	 
