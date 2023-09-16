
from py5paisa.order import Order, OrderType, Exchange
import pandas as pd
import time as tym
from datetime import datetime, date, time
import pytz # for timezone

def order_place(client, iDict, oDict):
########## ORDER PLACEMENT BUY/SELL AND STOPLOSS#########
    rec=pd.DataFrame()
    print("CE BUY order placed")
    r=client.place_order(OrderType='B',Exchange='N',ExchangeType='D',
                   ScripCode= int(CE_Scripcode_BUY),
                   Qty=qty, DisQty=qty, IsIntraday= False, IsStopLossOrder= False,
                    StopLossPrice=0, Price= 0,AHPlaced='N')   ## To place CE Buy
    rec1=pd.json_normalize(r)
    rec=pd.concat([rec,rec1])
    print("PE BUY order placed")
    r=client.place_order(OrderType='B',Exchange='N',ExchangeType='D',
                   ScripCode= int(PE_Scripcode_BUY),
                   Qty=qty, DisQty=qty, IsIntraday= False, IsStopLossOrder= False,
                    StopLossPrice=0, Price= 0, AHPlaced='N')  ## To place PE Buy
    rec1=pd.json_normalize(r)
    rec=pd.concat([rec,rec1])
    tym.sleep(Delay_buy) #to add delay between buy and sell
    print("CE SELL order placed")
    r=client.place_order(OrderType='S',Exchange='N',ExchangeType='D',
                   ScripCode = int(CE_Scripcode_SELL),
                   Qty=qty, DisQty=qty, IsIntraday= False, IsStopLossOrder= False,
                    StopLossPrice=0, Price= 0, AHPlaced='N') ## To place CE Sell
    rec1=pd.json_normalize(r)
    rec=pd.concat([rec,rec1])
    tym.sleep(Delay_buy) #to add delay between sell and sell
    print("PE SELL order placed")
    r=client.place_order(OrderType='S',Exchange='N',ExchangeType='D',
                   ScripCode = int(PE_Scripcode_SELL),
                   Qty=qty, DisQty=qty, IsIntraday= False, IsStopLossOrder= False,
                    StopLossPrice=0, Price= 0, AHPlaced='N') ## To place PE Sell
    rec1=pd.json_normalize(r)
    rec=pd.concat([rec,rec1])
    tym.sleep(Delay_buy)
    #################### Placing Stoploss Order ######################

    tym.sleep(20)
    df_pos=pd.json_normalize(client.positions())
    for i in range(len(df_pos.index)):
        if df_pos['NetQty'][i]<0:
            print("SL order placed")
            r=client.place_order(OrderType='B',Exchange='N',ExchangeType='D', ScripCode = int(df_pos['ScripCode'][i]),
                                Qty=int(abs(df_pos['NetQty'][i])), DisQty=0, 
                                Price=int(round(df_pos['SellAvgRate'][i]*Stop_loss*1.1,0)),
                                IsIntraday=False, StopLossPrice=int(Stop_loss*df_pos['SellAvgRate'][i]), 
                                AHPlaced='N')
            rec1=pd.json_normalize(r)
            rec=pd.concat([rec,rec1])
    return rec
# Request details
## OrderType: B-Buy, S- Sell
## Exchange: N- NSE, B- BSE, M- Mcx
## ExchangeType: C- Cash, D- Derivative, U-Currency
## ScripCode: Refer to scrip master file.
## Qty: No. of units to trade
## Price: Price at which order is to be placed. If Price is set 0, Order is treated as market order.
## IsIntraday: True/False
## IsStopLossOrder: True/False
## StopLossPrice: Trigger Price to be set. If Stop Loss Price is set  0, Order becomes Stop Loss Order).
                                                                                   #This is non complusory input.
## AHPlaced: After Market order confirmation. Y: Yes, N: No

#Response details:
##BrokerOrderID: BrokerOrderID of order placed
##ClientCode: ClientCode passed in request
##Exch: Exchange passed in request, N- NSE, B- BSE, M- Mcx
##ExchOrderID: it comes as zero RMS doesnt send Exchange order ID
##ExchType: Exchange Type passed in request, C- Cash, D- Derivative, U-Currency
##LocalOrderID: OrderID passed in request
##Message: Error Message
##RMSResponseCode: RMSResponseCode
##RemoteOrderID:
##Scripcode: Scripcode passed in request
##status: status of order request
##time: order placed time