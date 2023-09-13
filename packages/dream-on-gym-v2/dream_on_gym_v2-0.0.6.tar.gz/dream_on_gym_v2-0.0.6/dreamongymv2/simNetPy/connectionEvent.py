class ConnectionEvent:
    def __init__(self):
        self.__source = None
        self.__destination = None
        self.__bitRate = None
        self.__idConnection = None
    
    @property
    def source(self):
        return self.__source
    
    @source.setter
    def source(self,value):
        self.__source = value

    @property
    def destination(self):
        return self.__destination
    
    @destination.setter
    def destination(self,value):
        self.__destination = value

    @property
    def bitRate(self):
        return self.__bitRate
    
    @bitRate.setter
    def bitRate(self,value):
        self.__bitRate = value
    
    @property
    def idConnection(self):
        return self.__idConnection
    
    @idConnection.setter
    def idConnection(self,value):
        self.__idConnection = value