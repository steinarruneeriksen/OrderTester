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

TradeIdGen.tradeIdNum=0
DealIdGen.dealId=0

def resetPrecondition():
    ob=Orderbook()  #Add 3 buy and 3 sell orders all for 5 MW

    #Second parameter 1..5 is participant id
    ob.enterOrder(Order(0,"Mitnetz", 24, None, None, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    ob.enterOrder(Order(0,"Mitnetz", 18, None, None, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT,isp, isp_end, expiration))
    ob.enterOrder(Order(0,"Mitnetz", 12, None, None, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    ob.enterOrder(Order(0,"FSP1", None, 10, 27, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    ob.enterOrder(Order(0,"FSP2", None, 10, 28, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    ob.enterOrder(Order(0,"FSP3", None, 5, 37,  5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT,isp, isp_end, expiration))
    return ob

def genTest(description, o):

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
    print("Trades")
    for trade in t.postcondition.trades:
        print json.dumps(trade,default=convert_to_dict,indent=4, sort_keys=True)
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

    participant="Test Aggressor" # Agressor participant (6). Participants 1..5 are already given on the passive precondition orders

    genTest("Buy Order", Order(0,participant, 37, None, None, 50, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))

    #genTest("Buy Order", Order(0,participant, 25, None, None, 2, FillTypeEnum.FAK, PriceTypeEnum.LIMIT, isp, isp_end, expiration))
    #genTest("Sell Order", Order(0,participant, None, 5, 5, 8, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))

    #genTest("Sell Order", Order(0,participant, None, 5, 5, 5, FillTypeEnum.NORMAL, PriceTypeEnum.LIMIT, isp, isp_end, expiration))


    #Generate lots of combinations as seller into the precondition
    # for a in FillTypeEnum:
    #     #for b in PriceTypeEnum:    Market pricetype not allowed for FSP Asset selling.....
    #     b=PriceTypeEnum.LIMIT
    #     for qty in [5,15,75]:
    #         for aprice in [10, 20,30]:  #Keeping reservation price fixed and changing activation price on sell orders
    #             desc="Sell;" + FILLTYPES[a] + ";" + PRICETYPES[b] + ";" + str(qty) + ";" + str(5 + aprice)
    #             genTest(desc, Order(0, participant, None, 5, aprice, qty, a, b, isp, isp_end, expiration))
    #
    # #Generate lots of combinations as buyer into the precondition
    # for a in FillTypeEnum:
    #     for b in PriceTypeEnum:
    #         for qty in [5,15,75]:
    #             for unitPrice in [10, 20,30]:
    #                 desc="Buy;" + FILLTYPES[a] + ";" + PRICETYPES[b] + ";" + str(qty) + ";" + str(5 + unitPrice)
    #                 genTest(desc, Order(0,participant, unitPrice, None, None, qty, a, b, isp, isp_end, expiration))

    # f=open(TestMaster.targetdir + "testdata.csv","w")
    # f.write("Test file;Buy or Sell;Fill type;Order type;Quantity;Price\n")
    # f.write(TestMaster.csv)
    # f.close()


    TestMaster.html+="</body></html>"
    f=open(TestMaster.targetdir + "OrderData.html","w")
    f.write(TestMaster.html)
    f.close()