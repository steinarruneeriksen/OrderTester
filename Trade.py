__author__ = 'steinarruneeriksen'
from Globals import TradeIdGen


class Trade:

    def __init__(self):
        self.tradeId=0#TradeIdGen.tradeIdNum
    def getReservePriceReceivable(self):
        try:
            return self.reservePriceReceivable
        except:
            return 0

    def getReservePricePayable(self):
        try:
            return self.reservePricePayable
        except:
            return 0
    def getActivationPriceReceivable(self):
        try:
            return self.activationPriceReceivable
        except:
            return 0

    def getActivationPricePayable(self):
        try:
            return self.activationPricePayable
        except:
            return 0