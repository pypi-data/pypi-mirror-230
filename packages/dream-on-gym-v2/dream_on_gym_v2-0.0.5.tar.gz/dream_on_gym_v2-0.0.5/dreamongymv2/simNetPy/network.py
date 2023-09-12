# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 17:51:19 2022

@author: redno
"""
from .filemanager.readerJson import Reader
import sys
sys.path.append('../')


class Network:

    def __init__(self, filename):
        self.__linkCounter = 0
        self.__nodeCounter = 0
        self.__nodes = []
        self.__links = []
        self.__linksIn = []
        self.__linksOut = []
        self.__nodesIn = []
        self.__nodesOut = []
        self.__nodesIn.append(0)
        self.__nodesOut.append(0)

        # Open JSON File
        j = Reader()
        j.readNetwork(filename, self.nodes, self.links)
        # Number of Nodes
        self.__nodeCounter = len(self.nodes)
        self.__linkCounter = len(self.links)
        outCount = 0
        inCount = 0
        for i in range(self.nodeCounter):
            for j in range(self.linkCounter):
                if (i == self.links[j].src):
                    self.__linksOut.append(self.links[j])
                    outCount = outCount + 1
                if (i == self.links[j].dst):
                    self.__linksIn.append(self.links[j])
                    inCount = inCount + 1
            self.nodesOut.append(outCount)
            self.nodesIn.append(inCount)

    def addNode(self, node):
        if (node._id != self.__nodeCounter):
            raise("Cannot add a Node to this network with Id mismatching node counter.")
        self.__nodeCounter = self.nodeCounter + 1
        self.nodes.append(node)
        self.nodesIn.append(0)
        self.nodesOut.append(0)

    def addLink(self, link):
        if (link._id != self.linkCounter):
            raise("Cannot add a Link to this network with Id mismatching link counter.")
        self.__linkCounter = self.linkCounter + 1
        self.links.append(link)

    def connect(self, src, linkPos, dst):
        if (src < 0 or src >= self.__nodeCounter):
            raise("Cannot connect src "+src +
                  " because its ID is not in the network. Number of nodes in network: "+self.__nodeCounter)
        if (dst < 0 or dst >= self.__nodeCounter):
            raise("Cannot connect dst "+dst +
                  " because its ID is not in the network. Number of nodes in network: "+self.__nodeCounter)
        if (linkPos < 0 or linkPos >= self.__linkCounter):
            raise("Cannot use link "+linkPos +
                  " because its ID is not in the network. Number of links in network: "+self.__linkCounter)
        self.__linksOut.insert(
            self.linksOut[0] + self.nodesOut[src], self.links[linkPos])
        for n in range(self.nodesOut[0] + src + 1, self.nodesOut[-1]):
            self.nodesOut[n] = self.nodesOut[n] + 1
        self.__linksIn.insert(
            self.linksIn[0] + self.__nodesIn[dst], self.links[linkPos])
        for n in range(self.nodesIn[0] + dst + 1, self.nodesIn[-1]):
            self.nodesIn[n] = self.nodesIn[n] + 1
        self.links[linkPos]._src = src
        self.links[linkPos]._dst = dst

    def isConnected(self, src, dst):
        for i in range(self.__nodesOut[src], self.__nodesOut[src+1]):
            for j in range(self.__nodesIn[dst], self.__nodesIn[dst+1]):
                if(self.__linksOut[i].id == self.__linksIn[j].id):
                    return self.__linksOut[i].id
        return -1

    def useSlot(self, linkPos, slotFrom, slotTo = None, bandSelected = "NoBand"):
        self.links[linkPos].bandSelected = bandSelected
        if (slotTo is None):
            if (linkPos < 0 or linkPos > self.__linkCounter):
                raise("Link position out of bounds.")
            if (self.links[linkPos].slots[slotFrom] == True):
                raise("Bad assignation on slot",slotFrom)
            self.links[linkPos].slots[slotFrom] = True
        else:
            self.validateSlotFromTo(linkPos, slotFrom, slotTo)
            for i in range(slotFrom, slotTo):
                self.links[linkPos].slots[i] = True

    def unuseSlot(self, linkPos, slotFrom, slotTo = None, bandSelected = "NoBand"):
        self.links[linkPos].bandSelected = bandSelected
        if (slotTo is None):
            if (linkPos < 0 or linkPos > self.__linkCounter):
                raise("Link position out of bounds.")
            self.links[linkPos].slots[slotFrom] = False
        else:
            self.validateSlotFromTo(linkPos, slotFrom, slotTo)
            for i in range(slotFrom, slotTo):
                self.links[linkPos].slots[i] = False

    def isSlotUsed(self, linkPos, slotPos):
        if (linkPos < 0 or linkPos >= self.linksCounter):
            raise("Link position out of bounds.")
        if (slotPos < 0 or slotPos >= self.links[linkPos].getSlots()):
            raise("slot position out of bounds.")
        return self.links[linkPos].slots[slotPos]

    def validateSlotFromTo(self, linkPos, slotFrom, slotTo):
        if (linkPos < 0 or linkPos >= self.linkCounter):
            raise("Link position out of bounds.")
        if (slotFrom < 0 or slotFrom >= self.links[linkPos].getSlots()):
            print("slot position out of bounds. (From Slot",slotFrom,") of ",self.links[linkPos].getSlots())
            raise("slot position out of bounds.")
        if (slotTo < 0 or slotTo > self.links[linkPos].getSlots()):
            print("slot position out of bounds. (To Slot", slotTo, ") of ",self.links[linkPos].getSlots())
            raise("slot position out of bounds.")
        if (slotFrom > slotTo):
            raise("Initial slot position must be lower than the final slot position.")
        if (slotFrom == slotTo):
            raise("Slot from and slot To cannot be equals.")

    def getNumberOfNodes(self):
        return self.__nodeCounter

    def getNumberOfLinks(self):
        return self.__linkCounter

    def getLink(self, idLink):
        return self.__links[idLink]

    ''' '''
    @property
    def linkCounter(self):
        return self.__linkCounter

    ''' '''
    @property
    def nodeCounter(self):
        return self.__nodeCounter

    ''' '''
    @property
    def nodes(self):
        return self.__nodes
    
    ''' '''
    @property
    def links(self):
        return self.__links

    ''' '''
    @property
    def linksIn(self):
        return self.__linksIn

    ''' '''
    @property
    def linksOut(self):
        return self.__linksOut

    ''' '''
    @property
    def nodesIn(self):
        return self.__nodesIn

    ''' '''
    @property
    def nodesOut(self):
        return self.__nodesOut