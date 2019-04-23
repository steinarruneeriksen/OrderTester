__author__ = 'steinarruneeriksen'
from Globals import OrderIdGen
from MarketEnums import *
from json_convert_to_dict import convert_to_dict
import json
import copy

# 2 different order functions. Sorting buy orders with highest price on top and sell orders with lowest price on top

def cmp_items_buyers(a, b):
    if a.orderParameters.getSumPrice() < b.orderParameters.getSumPrice():
        return 1
    elif a.orderParameters.getSumPrice() == b.orderParameters.getSumPrice():
        return 0
    else:
        return -1

def cmp_items_sellers(a, b):
    if a.orderParameters.getSumPrice() > b.orderParameters.getSumPrice():
        return 1
    elif a.orderParameters.getSumPrice() == b.orderParameters.getSumPrice():
        return 0
    else:
        return -1


class Orderbook:

    def __init__(self):
        OrderIdGen.orderIdNum=100  #Initialize Order Id singleton
        self.buy_orders=[]
        self.sell_orders=[]
        
    #Appends to correct list and sorts using the correct Buy/Sell option    
    def updateAndSort(self, orderList, order, sortfunc):
        orderList.append(order)
        orderList.sort(sortfunc)

    #Calls SIngleton to increment global ID and assigns it
    def genOrderId(self, order):
        OrderIdGen.orderIdNum+=1
        order.orderParameters.orderId=OrderIdGen.orderIdNum


    def updateOrderStatus(self, orders, id, status):
        for o in orders:
            if o.orderParameters.orderId==id:
                o.orderParameters.orderStatus=ORDERSTATUSES[status]

    # Takes either buy or sell side and filters correct types
    # Only match against ACTIVE orders, i.e. do not match against already filled orders
    def applyFilters(self, orderList, quantityType, regulation):
        retList=[]
        for o in orderList:
            if o.orderParameters.orderStatus==OrderStatusEnum.ACTIVE and \
                            o.orderParameters.quantityType==quantityType and \
                            o.orderParameters.regulation==regulation :
                retList.append(o)
        return retList

    def genOrderActionHtml(self, o):
        ostr="Side<b>: " + str(o.orderParameters.side) + "</b>"
        if o.isBuyOrder():
            ostr+=" UnitPrice: <b>" + str(o.orderParameters.unitPrice) + "</b>"
        else:
            ostr+=" ReservPrice: <b>" + str(o.orderParameters.reservationPrice) + "</b> ActPrice: <b>" + str(o.orderParameters.activationPrice)  + " </b>= sum(" + str(o.orderParameters.getSumPrice()) + ")"
        ostr+=" FillType: <b>" + str(o.orderParameters.fillType)+ "</b>"
        ostr+=" PriceType: <b>" + str(o.orderParameters.priceType)+ "</b>"
        return ostr

    def getHtmlOrderTables(self):
        tbl="<b>Buy Orders</b>"
        tbl=tbl+"<table class='ordertable'><tr><th>OrderId</th><th>HistOrderId</th><th>Status</th><th>Price</th><th>Qty</th></tr>"
        for o in self.buy_orders:
            tbl=tbl+ self.debugHtmlOrder(o)
        tbl+="</table>"

        tbl+="<b>Sell Orders</b>"
        tbl=tbl+"<table class='ordertable'><tr><th>OrderId</th><th>HistOrderId</th><th>Status</th><th>Price</th><th>Qty</th></tr>"
        for o in self.sell_orders:
            tbl=tbl+ self.debugHtmlOrder(o)
        tbl=tbl+"</table>"
        return tbl
    
    def debugHtmlOrder(self, o):
        return "<tr><td>" + str(o.orderParameters.orderId) + "</td><td>" + str(o.orderParameters.histOrderId) + "</td><td>" + o.orderParameters.orderStatus \
        + "</td><td>" + str(o.orderParameters.getSumPrice()) + "</td><td>" + str(o.orderParameters.quantity) + "</td></tr>"

    def debugSingleOrder(self, o):
        return "OID: " + str(o.orderParameters.orderId) + ",HistOID: " + str(o.orderParameters.histOrderId) + ",STATUS: " + o.orderParameters.orderStatus \
        + ",PRICE: " + str(o.orderParameters.getSumPrice()) + ",QTY: " + str(o.orderParameters.quantity)

    def debugAllOrders(self):
        print "BUY Orders:"
        for o in self.buy_orders:
            print self.debugSingleOrder(o)

        print "SELL Orders:"
        for o in self.sell_orders:
            print self.debugSingleOrder(o)

    def debugAsJson(self, o):
        print json.dumps(o,default=convert_to_dict,indent=4, sort_keys=True)

    def enterOrder(self, o):
        #Just in case FoK/FaK means it will not transact. Hence prepare list and commit at end
        tempNewSplitdOrders=[]
        tempFilledOrders=[]
        tempCancelledOrders=[]

        self.genOrderId(o)
        qtyToFill=o.orderParameters.quantity  #qtyToFill will be reduced until fully filled or not more orders to fill from

        if o.isBuyOrder():
            passive_orders=self.sell_orders   #Set orders to match against (if buy then match against sell
            aggressor_orders=self.buy_orders
            cmp_function_passorders=cmp_items_sellers
            cmp_function_aggorders=cmp_items_buyers
        else:
            passive_orders=self.buy_orders
            aggressor_orders=self.sell_orders
            cmp_function_passorders=cmp_items_buyers
            cmp_function_aggorders=cmp_items_sellers

        self.updateAndSort(aggressor_orders, o, cmp_function_aggorders)

        subset=self.applyFilters(passive_orders, o.orderParameters.quantityType, o.orderParameters.regulation)
        for order in subset:
            #Fill quantity but not higher than LimitPrice (Or if Market order is used then disregard price limit)
            fillOrder=False
            if o.isBuyOrder():
                if (o.orderParameters.getSumPrice()>=order.orderParameters.getSumPrice() or o.orderParameters.priceType==PRICETYPES[PriceTypeEnum.MARKET]) and qtyToFill>0:
                    fillOrder=True
            else:
                if (o.orderParameters.getSumPrice()<=order.orderParameters.getSumPrice() or o.orderParameters.priceType==PRICETYPES[PriceTypeEnum.MARKET]) and qtyToFill>0:
                    fillOrder=True
            if fillOrder:
                if qtyToFill>=order.orderParameters.quantity:
                    tempFilledOrders.append(order)
                    qtyToFill=qtyToFill-order.orderParameters.quantity
                elif qtyToFill<order.orderParameters.quantity:
                    # Split the passive order, and set the filled part as the old ID and
                    tempCancelledOrders.append(order)   # The old order swill be cancelled
                    restQuantity=order.orderParameters.quantity-qtyToFill
                    passiveOrder1 = copy.deepcopy(order)
                    passiveOrder2 = copy.deepcopy(order)
                    passiveOrder1.orderParameters.histOrderId=order.orderParameters.orderId
                    passiveOrder2.orderParameters.histOrderId=order.orderParameters.orderId
                    self.genOrderId(passiveOrder1)
                    self.genOrderId(passiveOrder2)
                    passiveOrder2.orderParameters.quantity=restQuantity
                    passiveOrder2.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.ACTIVE]
                    passiveOrder1.orderParameters.quantity=qtyToFill
                    passiveOrder1.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.FILLED]

                    tempNewSplitdOrders.append(passiveOrder1)    #Will be added to the main sellers list if not rolled back (FillorKill case)
                    tempNewSplitdOrders.append(passiveOrder2)
                    #self.updateAndSort(self.sell_orders, o2, cmp_items_sellers)
                    qtyToFill=0   #Was completely filled

        transactFills=True

        if qtyToFill==0:  # The aggressor buyer was fully matched
            o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.FILLED]
        else:
            #print "Aggressor was not entirely matched"
            if o.orderParameters.fillType==FILLTYPES[FillTypeEnum.FOK]:              #ROLLBACK. Set aggressor to expired
                o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.EXPIRED]
                transactFills=False
            elif o.orderParameters.quantity==qtyToFill and o.orderParameters.fillType==FILLTYPES[FillTypeEnum.NORMAL]:
                #Nothing was filled and type was Normal. Just leave as Active
                pass
            else:
                #Split aggressor, and add orig order to cancel queue
                o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.CANCELLED]
                o1 = copy.deepcopy(o)
                o2 = copy.deepcopy(o)
                filledQuantity=o.orderParameters.quantity-qtyToFill

                o1.orderParameters.quantity=filledQuantity
                o2.orderParameters.quantity=qtyToFill   #Remaining quantity

                o1.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.FILLED]
                o2.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.ACTIVE]  #Remain in orderbook if not FAK

                self.genOrderId(o1)
                self.genOrderId(o2)
                o1.orderParameters.histOrderId=o.orderParameters.orderId
                o2.orderParameters.histOrderId=o.orderParameters.orderId

                if o.orderParameters.fillType==FILLTYPES[FillTypeEnum.FAK]:
                    o2.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.EXPIRED]

                self.updateAndSort(aggressor_orders, o1, cmp_function_aggorders)
                self.updateAndSort(aggressor_orders, o2, cmp_function_aggorders)

        #If FoK rolled back transactionm, do nothing, otherwise update passive and aggressor orders
        if transactFills:
            for ord in tempFilledOrders:
                ord.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.FILLED]
            for ord in tempCancelledOrders:
                ord.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.CANCELLED]
            for newSplitOrder in tempNewSplitdOrders:  #THe newly created orders (if any) from splits
                self.updateAndSort(passive_orders, newSplitOrder, cmp_function_passorders)

