__author__ = 'steinarruneeriksen'

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class OrderIdGen(object):
    __metaclass__ = Singleton

class TestMaster(object):
    __metaclass__ = Singleton

class TradeIdGen(object):
    __metaclass__ = Singleton
