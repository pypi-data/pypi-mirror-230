# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 15:29:56 2022

@author: redno
"""
# from .allocator import Allocator
import string

from .network import Network
from .connection import Connection
import enum
import json

### modify access to private variables of Connections & Network classes


class Controller:

    def __init__(self, network=None):
        self.__connections = []
        self.__allocator = None
        self.__network = network
        self.__path = []

    ''' Check privacy of status // __status return error with N_A when calling getter in Simulator '''
    Status = enum.Enum('Status','Allocated Not_Allocated N_A')

    # @property
    # def allocator(self):
    #     return self.__allocator

    # @allocator.setter
    # def allocator(self, allocator):
    #     self.__allocator = allocator

    def assignConnection(self, src, dst, bitRate, idConnection, action = None):
        con = Connection(idConnection)

        # Problema inicial, faltaban dos argumentos network y path, la solucion torpe es agregarlos pero no usarlos
        # actualización estas variables deben entrar
        rtnAllocation, con = self.__allocator(
            src, dst, bitRate, con, self.__network, path=self.__path, action=action)
        if (rtnAllocation.name == Controller.Status.Allocated.name):
            self.__connections.append(con)
            for j in range(0, len(con.links)):
                self.__network.useSlot(con.links[j].id, con.slots[j][0], con.slots[j][0]+len(con.slots[j]), con.bandSelected)

        return rtnAllocation

    def unassignConnection(self, idConnection):
        for i in range(0, len(self.__connections)):
            if (self.__connections[i].id == idConnection):
                con = self.__connections[i]
                for j in range(0, len(con.links)):
                    self.__network.unuseSlot(con.links[j].id, con.slots[j][0], con.slots[j][0]+len(con.slots[j]), con.bandSelected)
                
                self.__connections.pop(i)
                break

        return 0

    def setPaths(self, filename):
        with open(filename) as json_file:
            filePaths = json.load(json_file)
        numberOfNodes = self.__network.getNumberOfNodes()
        self.__path = []

        for i in range(0, numberOfNodes):
            self.__path.append([])
            for j in range(0, numberOfNodes):
                self.__path[i].append([])
        routesNumber = len(filePaths['routes'])

        for i in range(0, routesNumber):
            # Numero de caminos
            #     "paths": [
            #     [0, 1],
            #     [0, 2, 1],
            #     [0, 7, 6, 4, 3, 1]
            #   ]
            pathsNumber = len(filePaths['routes'][i]['paths'])

            # "src": 0,
            src = filePaths['routes'][i]['src']

            # "dst": 1,
            dst = filePaths['routes'][i]['dst']
            for j in range(0, pathsNumber):
                self.__path[src][dst].append([])
            for j in range(0, pathsNumber):
                # ubicación de un camino
                #   "paths": [
                #     [0, 1],      <---- este por ejemplo
                #     [0, 2, 1],
                #     [0, 7, 6, 4, 3, 1]
                #   ]
                nodesPathNumber = len(filePaths['routes'][i]['paths'][j])
                lastNode = nodesPathNumber - 1
                for k in range(0, lastNode):
                    actNode = filePaths['routes'][i]['paths'][j][k]
                    nextNode = filePaths['routes'][i]['paths'][j][k+1]
                    idLink = self.__network.isConnected(actNode, nextNode)

                    self.__path[src][dst][j].append(
                        self.__network.getLink(idLink))
        return 0

    def getConnection(self, idConnection):
        for i in range(len(self.__connections)):
            if self.__connections[i].id == idConnection:
                return self.__connections[i]
        return None
    ''' '''
    @property
    def connections(self):
        return self.__connections

    @connections.setter
    def connections(self,connection):
        self.__connections.append(connection)

    ''' '''
    @property
    def allocator(self):
        return self.__allocator

    @allocator.setter
    def allocator(self, allocator):
        self.__allocator = allocator

    ''' '''
    @property
    def network(self):
        return self.__network

    @network.setter
    def network(self, network):
        self.__network = network 

    ''' '''
    @property
    def path(self):
        return self.__path

    ''' '''
    #@property
    #def Status(self):
    #    return self.__Status