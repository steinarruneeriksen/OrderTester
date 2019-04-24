__author__ = 'steinarruneeriksen'
from Globals import TradeIdGen


class Trade:

    def __init__(self):
        TradeIdGen.tradeIdNum+=1
        self.tradeId=TradeIdGen.tradeIdNum
