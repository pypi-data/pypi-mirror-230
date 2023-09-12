# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 14:37:03 2022

@author: redno
"""


class Link:
    __id = -1
    __length = 1
    __slots = None
    __src = -1
    __dst = -1

    def __init__(self, id=-1, length=1, slots=-1, bands=None):
        self.__id = id
        self.__length = length
        self.__slots = {}
        self.__slots["NoBand"] = []
        self.__slots["L"] = []
        self.__slots["C"] = []
        self.__slots["S"] = []
        self.__slots["E"] = []
        self.__slots["O"] = []
        self.__bandSelected = "NoBand"

        if bands is None:
            for _ in range(slots):
                self.__slots['NoBand'].append(False)
        else:
            for key in bands:
                for _ in range(bands[key]):
                    self.__slots[key].append(False)       
        self.__src = -1
        self.__dst = -1

    def setSlots(self, slots, band = None):
        # Search if slots are used.
        if band is None:
            slotsAux = self.__slots[self.__bandSelected]
        else:
            slotsAux = self.__slots[band]
        
        for slot in slotsAux:
            if slot == True:
                break

        if slots > len(slotsAux):
            for x in range(slots-len(slotsAux)):
                slotsAux.append(False)

        else:
            for x in range(len(slotsAux)-slots):
                del slotsAux[0]
                
    def getBands(self):
        bands = []
        for key in range(self.__slots):
            if self.__slots[key] > 0:
                bands.append(key)
                
    def isBandEnabled(self, band):
        for key in range(self.__slots):
            if (key == band) and (self.__slots[key] > 0):
                return True
        return False

    def getSlots(self, band = None):
        if band is None:
            return len(self.__slots[self.__bandSelected])
        else:
            return len(self.__slots[band])

    def getSlot(self, idSlot, band = None):
        if band is None:
            return self.__slots[self.__bandSelected][idSlot]
        else:
            return self.__slots[band][idSlot]
        
    def info(self, band = None):
        print("ID: ", self.__id)
        print("Ancho", self.__length)
        print("Se muestra el estado de los slots")
        if band is None:
            for slot in self.__slots[self.__bandSelected]:
                print(slot)
        else:
            for slot in self.__slots[band]:
                print(slot)
        print("Fuente: ", self.__src, " - Destino: ", self.__dst)


    ''' 
        Spectrum band get and set default functions 
        Set value for band with object.band = VALUE
        Then call object.slots to get the slots array  
    '''
    @property
    def bandSelected(self):
        return self.__bandSelected
    
    @bandSelected.setter
    def bandSelected(self,band=None):
        if band is None:
            self.__bandSelected = "NoBand"
        else:
            self.__bandSelected = band

    ''' '''
    @property
    def slots(self):
        return self.__slots[self.__bandSelected]

    @slots.setter
    def slots(self,band,slots):
        self.__slots[band] = slots
            

    ''' '''
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self,id):
        self.__id = id

    ''' '''
    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self,length):
        self.__length = length

    ''' '''
    @property
    def src(self):
        return self.__src

    @src.setter
    def src(self,src):
        self.__src = src

    ''' '''
    @property
    def dst(self):
        return self.__dst

    @dst.setter
    def dst(self,dst):
        self.__dst = dst