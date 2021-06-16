

from typing import Type


class Order(object):

    class Action:
        BUY = 0
        SELL = 1

    class Type:
        MARKET = 'MARKET'
        LIMIT = 'LIMIT'
        STOP = 'STOP'

    __id = None
    __action = None
    __symbol = None
    __type = None

    __level = None
    __stop_distance = None
    __stop_level = None
    __limit_distance = None
    __limit_level = None

    @property
    def action(self)->Action:
        return self.__action

    @property
    def level(self):
        return self.__level

    @property
    def limitDistance(self):
        return self.__limit_distance

    @property
    def limitLevel(self):
        return self.__limit_level

    @property
    def id(self):
        return self.id

    @property
    def type_(self)->Type:
        return self.__type

    @property
    def stopDistance(self):
        return self.__stop_distance

    @property
    def stopLevel(self):
        return self.__stop_level

    @property
    def symbol(self):
        return self.__symbol

    def router(self):
        '''
        router class is the interface that connects the Order class with each broker.
        '''
        raise NotImplementedError()

    