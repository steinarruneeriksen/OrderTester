__author__ = 'steinarruneeriksen'
import json
import datetime
from MarketEnums import *
import datetime as dt
import random
format = "%Y-%m-%dT%H:%M:%S.%f"

class OrderParameters():

    # In order to match orders, we either take UnitPrice (buy orders) or sum of Activation and Reservation price
    def getSumPrice(self):
        if self.unitPrice is None:
            return self.activationPrice + self.reservationPrice
        else:
            return self.unitPrice

    # unitPrice used for Buy Orders.
    def __init__(self, id, unitPrice, reservPrice, activPrice,quantity, fillType, priceType, expiration):
        self.orderId=id
        self.histOrderId=None     #Reference to historical order this order was changed/split from
        self.unitPrice=unitPrice
        self.activationPrice=activPrice
        self.reservationPrice=reservPrice
        if unitPrice is None:
            self.side=SIDES[SideEnum.SELL]
        else:
            self.side=SIDES[SideEnum.BUY]
        self.fillType=FILLTYPES[fillType]

        # Set order update time to a random set of minutes prior to expiration
        orderTime=expiration - dt.timedelta(minutes = random.randint(1, 300))
        self.createdUtc=orderTime.isoformat()
        self.lastModifiedUtc=orderTime.isoformat()
        self.orderStatus=ORDERSTATUSES[OrderStatusEnum.ACTIVE]
        self.currency="EUR"
        self.quantityType=QUANTITYTYPES[QuantityTypeEnum.POWER]
        self.quantity=quantity
        self.regulation=REGULATIONS[RegulationEnum.DOWN]
        self.priceType=PRICETYPES[priceType]
        self.expirationUtc=expiration.isoformat()


