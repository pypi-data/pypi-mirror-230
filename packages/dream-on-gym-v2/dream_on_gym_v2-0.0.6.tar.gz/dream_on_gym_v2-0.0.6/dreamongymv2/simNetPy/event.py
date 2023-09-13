# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 11:59:20 2022

@author: redno
"""

import enum


class EventType(enum.Enum):
    NoData = 1
    Arrive = 2
    Departure = 3


class Event:
    __eventType = EventType.NoData
    __time = -1
    __idConnection = -1

    def __init__(self, eventType, time, idConnection):
        self.__eventType = eventType
        self.__time = time
        self.__idConnection = idConnection

    def getTime(self):
        return self.__time

    def getType(self):
        return self.__eventType

    def getIdConnection(self):
        return self.__idConnection

    ''' '''
    @property
    def eventType(self):
        return self.__eventType

    @eventType.setter
    def evenType(self,evenType):
        self.__eventType = evenType

    ''' '''
    @property
    def time(self):
        return  self.__time

    @time.setter
    def time(self,time):
        self.__time = time
    
    ''' '''
    @property
    def idConnection(self):
        return self.__idConnection

    @idConnection.setter
    def idConnection(self,idConnection):
        self.__idConnection = idConnection