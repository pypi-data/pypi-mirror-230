# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 17:27:29 2022

@author: redno
"""

import gymnasium
from dreamongymv2.simNetPy.simulator import Simulator

class RlOnEnv(gymnasium.Env):
    def __init__(self, action_space = 5, observation_space = 2, start_training = 1000):
        self.action_space = gymnasium.spaces.Discrete(3)
        self.observation_space = gymnasium.spaces.Discrete(3)
        self.__simulator = None
        self.__rewardFunc = None
        self.__stateFunc = None
        self.__startTraining = start_training
        
    def start(self):
        #Inicia la simulación hasta el start_training, luego de eso pasa al paso a paso o reset.
        if self.__simulator is not None:
            self.__simulator.run()
            #for i in range(0)
    def step(self, action):
        if self.__simulator is not None: 
            #Se debe setear la acción tomada por el agente en el simulador.
            self.__simulator.step(action)
            self.__simulator.forwardDepartures()
            self.__simulator.createEventConnection()
            #Se debe recuperar el estado por omisión se deja 1
            if self.__stateFunc is not None:
                state = self.__stateFunc()
            else:
                state = 1
            if self.__rewardFunc is not None:
                reward = self.__rewardFunc()
            if self.__simulator.getTruncatedFunc() is not None:
                truncated = self.__simulator.TruncatedFunc()
            else:
                truncated = True
            if self.__simulator.getTerminatedFunc() is not None:
                terminated = self.__simulator.TerminatedFunc()
            else:
                terminated = True
        else:
            state = 1
            if action == 2:
                reward = 1
            else:
                reward = -1    
            truncated = True
            terminated = True
        
        info = {}
        return state, reward, terminated, truncated, info
    def reset(self, seed=None, options=None):
        #Se debe recuperar el estado al resetiar, por omisión se deja en 0
        state = 0
        info = {}
        return state, info
    
    def setStateFunc(self, func):
        self.__stateFunc = func
        
    def setRewardFunc(self, func):
        self.__rewardFunc = func
    
    def initEnviroment(self, networkFilename="", pathFilename="", bitrateFilename=""):
        self.__simulator = Simulator(networkFilename, pathFilename, bitrateFilename)
        
        self.__simulator.setGoalConnections(self.__startTraining)
    
    def getSimulator(self):
        return self.__simulator
        

        
