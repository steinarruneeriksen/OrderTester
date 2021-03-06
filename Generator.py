__author__ = 'steinarruneeriksen'
from Order import Order
from Orderbook import Orderbook
from json_convert_to_dict import convert_to_dict
import datetime as dt
import json
import copy
from MarketEnums import *
from Globals import TestMaster, TradeIdGen, DealIdGen
from Utils import htmlheader


class TestData:
    def __init__(self, description):
        self.description=description


isp = dt.datetime(2019,04,30,23,00,00)
isp_end=isp + dt.timedelta(minutes = 15)
expiration=isp - dt.timedelta(minutes = 15)

TestMaster.testnumber=1
TestMaster.csv=""
TestMaster.targetdir="/Users/steinarruneeriksen/OneDrive/testdata/"

TestMaster.html="<html><head>" + htmlheader + "</head><body>"



def resetPrecondition():
    ob=Orderbook()  #Add 3 buy and 3 sell orders all for 5 MW

    ob.enterOrder(Order(0,"Mitnetz", 24, None, None, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    ob.enterOrder(Order(0,"Mitnetz", 18, None, None, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT,isp, isp_end, expiration))
    ob.enterOrder(Order(0,"Mitnetz", 12, None, None, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    ob.enterOrder(Order(0,"FSP1", None, 10, 27, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    ob.enterOrder(Order(0,"FSP2", None, 10, 28, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    ob.enterOrder(Order(0,"FSP3", None, 5, 37,  5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT,isp, isp_end, expiration))
    return ob

def genTest(description, o):
    TradeIdGen.tradeIdNum=0
    DealIdGen.dealId=0

    TestMaster.html+="<h1>Test: "+ str(TestMaster.testnumber).zfill(3) + ".json;" + "</h1>"
    #TestMaster.html+="Json stored in " + str(TestMaster.testnumber).zfill(3) + ".json<p/>"
    t=TestData(description)
    t.precondition=resetPrecondition()
    TestMaster.html+=t.precondition.getHtmlOrderTables()
    copyOrderbook=copy.deepcopy(t.precondition)  # Will be altered by action
    t.orderAction=o

    TestMaster.html+="<br/><font color='darkred'><b>Action: Order added</b><br/>"
    TestMaster.html+=t.precondition.genOrderActionHtml(o)
    TestMaster.html+="</font><p/>"

    copyOrderbook.enterOrder(copy.deepcopy(o))
    t.postcondition=copyOrderbook
    t.postcondition.debugAllOrders()
    TestMaster.html+=t.postcondition.getHtmlOrderTables()
    TestMaster.html+=t.postcondition.getHtmlTradeTables()
    print("Testcase " + description  + ": testdata_" + str(TestMaster.testnumber).zfill(3) + ".json")
    csvstr=str(TestMaster.testnumber).zfill(3) + ".json;" + description
    TestMaster.csv=TestMaster.csv + csvstr + "\n"


    f=open(TestMaster.targetdir + str(TestMaster.testnumber).zfill(3) + ".json","w")
    f.write(json.dumps(t,default=convert_to_dict,indent=4, sort_keys=True))
    f.close()



    TestMaster.testnumber+=1

if __name__== "__main__":
    print "Staring generator"

    participant="Test Aggressor"


    #Uncommend lines below if you want to run separate tests
    #genTest("Buy Order", Order(0,participant, 38, None, None, 80, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    #genTest("Sell Order", Order(0,participant, None, 5, 10, 8, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))



    # #Generate lots of combinations as seller into the orderbook
    for fillType in FillTypeEnum:
        # Market pricetype not allowed for FSP Asset selling.....
        priceType=PriceTypeEnum.LIMIT
        for qty in [5,15,75]:
            activationPrice=12   #Keep same...
            for reservationPrice in [2, 5, 10]:  #Keeping reservation price fixed and changing activation price on sell orders
                desc="Sell;" + FILLTYPES[fillType] + ";" + PRICETYPES[priceType] + ";" + str(qty) + ";" + str(activationPrice + reservationPrice)
                genTest(desc, Order(0, participant, None, reservationPrice, activationPrice, qty, fillType, priceType, isp, isp_end, expiration))

    #Generate lots of combinations as buyer into the orderbook
    for fillType in FillTypeEnum:
        for priceType in PriceTypeEnum:
            for qty in [5,15,75]:
                for unitPrice in [10, 37, 38, 55]:
                    desc="Buy;" + FILLTYPES[fillType] + ";" + PRICETYPES[priceType] + ";" + str(qty) + ";" + str(unitPrice)
                    genTest(desc, Order(0,participant, unitPrice, None, None, qty, fillType, priceType, isp, isp_end, expiration))

    # f=open(TestMaster.targetdir + "testdata.csv","w")
    # f.write("Test file;Buy or Sell;Fill type;Order type;Quantity;Price\n")
    # f.write(TestMaster.csv)
    # f.close()


    TestMaster.html+="</body></html>"
    f=open(TestMaster.targetdir + "OrderData.html","w")
    f.write(TestMaster.html)
    f.close()