import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

class DQNLearner(object):
        def __init__(self):
            super().__init__()
        
            self._learning = True
            self._learning_rate = .1
            self._discount = .1
            self._epsilon = .9
            self.num_inputs = 4
            self.num_actions = 3
    
            # Create Model
            model = keras.Sequential()
            model.add(keras.Input(shape=(self.num_inputs,)))
            model.add(layers.Dense(24))
            model.add(layers.Activation('relu'))
    
            model.add(layers.Dense(24))
            model.add(layers.Activation('relu'))
    
            model.add(layers.Dense(self.num_actions))
            model.add(layers.Activation('linear'))
    
            #rms = RMSprop()
            model.compile(loss='mse', optimizer='adam')
            X = np.array([0,0,0,0])
            X = np.expand_dims(X,axis = 0)
            
            # y = np.array([0,0,0])
            # y = np.expand_dims(y,axis = 0)
            # model.fit(X,y,epochs = 1, batch_size = 1)
            print(model.predict(X)[0][0])
            self._model = model
        def update(self,qprime,state):
            self._model.fit(state,qprime, batch_size=4, epochs = 1,)
            
        
if __name__ == '__main__':
    DQNLearner()