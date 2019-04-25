__author__ = 'steinarruneeriksen'
from Globals import OrderIdGen, TradeIdGen, DealIdGen
from MarketEnums import *
from json_convert_to_dict import convert_to_dict
import json
import copy
from Trade import Trade

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
        self.trades=[]
        
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
            if o.orderParameters.orderStatus==ORDERSTATUSES[OrderStatusEnum.ACTIVE] and \
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
        ostr+=" Quantity: <b>" + str(o.orderParameters.quantity)+ "</b>"
        ostr+=" FillType: <b>" + str(o.orderParameters.fillType)+ "</b>"
        ostr+=" PriceType: <b>" + str(o.orderParameters.priceType)+ "</b>"
        return ostr

    def getHtmlOrderTables(self):
        tbl="<b>Buy Orders</b>"
        tbl=tbl+"<table class='ordertable'><tr><th>OrderId</th><th>HistOrderId</th><th>Status</th><th>Participant</th><th>Price</th><th>Qty</th><th>Orig Qty</th></tr>"
        for o in self.buy_orders:
            tbl=tbl+ self.debugHtmlOrder(o)
        tbl+="</table>"

        tbl+="<b>Sell Orders</b>"
        tbl=tbl+"<table class='ordertable'><tr><th>OrderId</th><th>HistOrderId</th><th>Status</th><th>Participant</th><th>Price</th><th>Qty</th><th>Orig Qty</th></tr>"
        for o in self.sell_orders:
            tbl=tbl+ self.debugHtmlOrder(o)
        tbl=tbl+"</table>"
        return tbl

    def getHtmlTradeTables(self):
        tbl="<b>Trades</b>"
        tbl=tbl+"<table class='tradetable'><tr><th>MatchId</th><th>TradeId</th><th>From Order</th><th>TradeTime</th><th>Paritipant</th><th>Side</th><th>Counterpart</th><th>Quantity</th><th>TotPrice</th><th>Settlement Reserve Price Payable</th><th>Settlement Reserve Price Receivable</th><th>ActivationPrice</th><th>Period</th></tr>"
        for o in self.trades:
            tbl=tbl+ self.debugHtmlTrade(o)
        tbl+="</table>"
        return tbl

    def debugHtmlTrade(self, t):
        return "<tr><td>" + str(t.dealId) + "</td><td>" + str(t.tradeId) + "</td><td>" + str(t.orderId)  + "</td><td>" + t.tradeTimeUtc \
        + "</td><td>" + t.participant + "</td><td>" + t.side + "</td><td>NODES</td><td>" + str(t.quantity)  + "</td><td>"+ str(t.totalPrice)  + "</td><td>"+ str(t.getReservePricePayable()) + "</td><td>" + str(t.getReservePriceReceivable()) + "</td><td>"+ str(t.activationPrice) + "</td><td>" + str(t.periodFromUtc) + " - " + str(t.periodUntilUtc) + "</td></tr>"

    def debugHtmlOrder(self, o):
        return "<tr><td>" + str(o.orderParameters.orderId) + "</td><td>" + str(o.orderParameters.histOrderId) + "</td><td>" + o.orderParameters.orderStatus \
        + "</td><td>" + o.participant + "</td><td>" + str(o.orderParameters.getPriceInfo()) + "</td><td>" + str(o.orderParameters.quantity)  + "</td><td>" + str(o.orderParameters.originalQuantity) + "</td></tr>"

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

    def getReservationPrice(self, order1, order2):
        if order1.orderParameters.reservationPrice is None:
            return order2.orderParameters.reservationPrice
        return order1.orderParameters.reservationPrice


    # Adds Trade record between agressor and passiove order, setting price as passive order (pay as bid), and settler the reservation price
    def createTrade(self, passiveOrder, agressorOrder):
        temptrades=[]
        DealIdGen.dealId+=1
        t=Trade()
        t.dealId=DealIdGen.dealId
        t.side=passiveOrder.orderParameters.side
        t.orderId=passiveOrder.orderParameters.orderId
        t.quantity=passiveOrder.orderParameters.quantity
        t.participant=passiveOrder.participant
        t.tradeTimeUtc=agressorOrder.orderParameters.lastModifiedUtc    #Trade time is same as order time of agressor
        t.counterpart="NODES"
        t.totalPrice=passiveOrder.orderParameters.getSumPrice()
        temptrades.append(t)

        t=Trade()
        t.dealId=DealIdGen.dealId
        t.orderId=agressorOrder.orderParameters.orderId
        t.side=agressorOrder.orderParameters.side
        t.participant=agressorOrder.participant
        t.tradeTimeUtc=agressorOrder.orderParameters.lastModifiedUtc
        t.counterpart="NODES"
        t.quantity=passiveOrder.orderParameters.quantity
        t.totalPrice=passiveOrder.orderParameters.getSumPrice()
        temptrades.append(t)

        # Just to make sure that the extra price in pay as bid is set on Reservation price
        payAsBidPremium=abs(agressorOrder.orderParameters.getSumPrice()-passiveOrder.orderParameters.getSumPrice())

        for t in temptrades:
            if t.side==SIDES[SideEnum.BUY]:
                t.reservePricePayable=self.getReservationPrice(passiveOrder, agressorOrder) + payAsBidPremium
            else:
                t.reservePriceReceivable=self.getReservationPrice(passiveOrder, agressorOrder) + payAsBidPremium
            t.activationPrice=(t.totalPrice-self.getReservationPrice(passiveOrder, agressorOrder))-payAsBidPremium
            t.blockSizeInSeconds=passiveOrder.timeParameters.blockSizeInSeconds
            t.periodFromUtc=passiveOrder.timeParameters.periodFromUtc
            t.periodUntilUtc=passiveOrder.timeParameters.periodUntilUtc
        return temptrades


    def enterOrder(self, o):
        #Just in case FoK/FaK means it will not transact. Hence prepare list and commit at end
        tempNewSplitdOrders=[]
        tempFilledOrders=[]
        tempCancelledOrders=[]
        tempTrades=[]
        priorDealId=DealIdGen.dealId

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

        # First filters all orders on the "passive side". Could have included Ramping etc also, but that is not part of this test case
        subset=self.applyFilters(passive_orders, o.orderParameters.quantityType, o.orderParameters.regulation)
        #Loop through all passive orders and match as much as possible...up until qtyToFill
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
                if qtyToFill>=order.orderParameters.quantity:   #Not completely filled on this iteratiom
                    tempFilledOrders.append(order)           # Will set this passive order to filled, ones we know it is not rolled back by FOK
                    tempTrades.extend(self.createTrade(order, o))   #Will also create a temp trade
                    qtyToFill=qtyToFill-order.orderParameters.quantity
                elif qtyToFill<order.orderParameters.quantity:
                    # Split the passive order, and set the filled part as the old ID and
                    restQuantity=order.orderParameters.quantity-qtyToFill
                    filledOrder = copy.deepcopy(order)
                    filledOrder.orderParameters.histOrderId=order.orderParameters.orderId
                    self.genOrderId(filledOrder)

                    order.orderParameters.quantity=restQuantity  #Orig Quantity holeds the orig quantity....
                    order.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.ACTIVE]

                    filledOrder.orderParameters.quantity=qtyToFill
                    filledOrder.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.FILLED]

                    # Generate trade record
                    tempTrades.extend(self.createTrade(filledOrder, o))
                    tempNewSplitdOrders.append(filledOrder)    #Will be added to the main sellers list if not rolled back (FillorKill case)
                    qtyToFill=0   #Was completely filled

        rollback=False

        if qtyToFill==0:  # The aggressor buyer was fully matched
            o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.FILLED]
        else:
            # The agressor was only partially filled. check what parameters he had specified (NORMAL, FOK or FAK)
            if o.orderParameters.fillType==FILLTYPES[FillTypeEnum.FOK]:              #ROLLBACK. Set aggressor to expired
                o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.EXPIRED]
                rollback=True
            elif o.orderParameters.quantity==qtyToFill and o.orderParameters.fillType==FILLTYPES[FillTypeEnum.NORMAL]:
                #Nothing was filled and type was Normal. Just leave as Active
                pass
            else:
                if o.orderParameters.fillType==FILLTYPES[FillTypeEnum.FAK] and qtyToFill==o.orderParameters.quantity:
                    o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.EXPIRED]  # No volume was filled... in FAK. just let expire
                else:
                    #Split aggressor, with filled part
                    o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.CANCELLED]
                    filledOrder = copy.deepcopy(o)
                    filledQuantity=o.orderParameters.quantity-qtyToFill

                    filledOrder.orderParameters.quantity=filledQuantity
                    o.orderParameters.quantity=qtyToFill   # Update order with Remaining quantity, orig quantity keeps original

                    filledOrder.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.FILLED]
                    o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.ACTIVE]  #Remain in orderbook if not FAK

                    self.genOrderId(filledOrder)
                    filledOrder.orderParameters.histOrderId=o.orderParameters.orderId

                    if o.orderParameters.fillType==FILLTYPES[FillTypeEnum.FAK]:
                        o.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.EXPIRED]
                    self.updateAndSort(aggressor_orders, filledOrder, cmp_function_aggorders)


        #If FoK rolled back transactionm, do nothing, otherwise update passive and aggressor orders
        if rollback==False:
            for ord in tempFilledOrders:
                ord.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.FILLED]
            for ord in tempCancelledOrders:
                ord.orderParameters.orderStatus=ORDERSTATUSES[OrderStatusEnum.CANCELLED]
            for newSplitOrder in tempNewSplitdOrders:  #THe newly created orders (if any) from splits
                self.updateAndSort(passive_orders, newSplitOrder, cmp_function_passorders)
            for trade in tempTrades:
                TradeIdGen.tradeIdNum+=1
                trade.tradeId=TradeIdGen.tradeIdNum
                self.trades.append(trade)
        else:
            DealIdGen.dealId=priorDealId # Reset

