__author__ = 'steinarruneeriksen'
from OrderParameters import OrderParameters
from TimeParameters import TimeParameters
from ProfileParameters import ProfileParameters
from LocationParameters import LocationParameters
import json
from MarketEnums import *


class Order():


    def __init__(self, id, participant,unitPrice, reservPrice, actPrice, quantity, fillType, priceType, ispFrom, ispUntil, expiration):
        self.orderParameters=OrderParameters(id, unitPrice, reservPrice, actPrice, quantity, fillType, priceType, expiration)
        self.timeParameters=TimeParameters(ispFrom,ispUntil)
        self.locationParameters=LocationParameters()
        self.participant=participant
        if unitPrice is None:
            self.profileParameters=ProfileParameters()
        else:
            self.profileParameters=None

    def isBuyOrder(self):
        if self.orderParameters.side==SIDES[SideEnum.BUY]:
            return True
        else:
            return False
    def getPriceInfo(self):
        self.orderParameters.getPriceInfo()
