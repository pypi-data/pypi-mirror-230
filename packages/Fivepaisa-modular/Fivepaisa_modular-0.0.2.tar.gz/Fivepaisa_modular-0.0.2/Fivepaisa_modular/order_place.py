from py5paisa.order import Order, OrderType, Exchange
import pandas as pd
import time as tym
from datetime import datetime, date, time
import pytz # for timezone

def order_place(client, iDict, oDict):
    
    CE_Scripcode_SELL=oDict['CE_Scripcode_SELL']
    CE_Scripcode_BUY=oDict['CE_Scripcode_BUY']
    PE_Scripcode_SELL=oDict['PE_Scripcode_SELL']
    PE_Scripcode_BUY=oDict['PE_Scripcode_BUY']
    
    qty=iDict['qty']
    buy_sell_order=iDict['buy_sell_order']
    same_day_sqoff=iDict['same_day_sqoff']
    Delay_buy=iDict['Delay_buy']
    Stop_loss=iDict['Stop_loss']
    squareoff_time=iDict['squareoff_time']
    
    
    rec=pd.DataFrame()
    
    if buy_sell_order=="BS":
        print("BUY AND SELL")
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
    
    if buy_sell_order=="SO":
        print("SELL ONLY")
    
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

    ################ Placing Stoploss Order ######################

    tym.sleep(10)
    df_pos=pd.json_normalize(client.positions())
    for i in range(len(df_pos.index)):
        if df_pos['NetQty'][i]<0:
            print("SL order placed")
            r=client.place_order(OrderType='B',Exchange='N',ExchangeType='D', ScripCode = int(df_pos['ScripCode'][i]),
                                Qty=int(abs(df_pos['NetQty'][i])), DisQty=0, 
                                Price=int(round(df_pos['SellAvgRate'][i]*Stop_loss*1.1,0)),
                                IsIntraday=False, StopLossPrice=int(df_pos['SellAvgRate'][i]*Stop_loss), 
                                AHPlaced='N')
            rec1=pd.json_normalize(r)
            rec=pd.concat([rec,rec1])


    ############## SAME DAY SL and AUTOSQUAREOFF CODE###########
    if same_day_sqoff=="E":
        print("Waiting for square-off at", squareoff_time)
        while True:
            tym.sleep(5)
            if squareoff_time<datetime.now(pytz.timezone('Asia/Kolkata')).time():
                print("Autosquareoff started at=",datetime.now(pytz.timezone('Asia/Kolkata')).time())
                client.squareoff_all()
                tym.sleep(5)
                client.squareoff_all()
            
    return rec
