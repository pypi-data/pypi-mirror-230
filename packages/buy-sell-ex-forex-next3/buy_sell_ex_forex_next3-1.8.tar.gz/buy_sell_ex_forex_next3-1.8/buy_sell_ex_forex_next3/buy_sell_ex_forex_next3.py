import MetaTrader5 as mt5

import json

from login_forex_next3 import Login
from tick_ex_forex_next3 import Tick

class BUY_SELL:
    
    def __init__(self):
       fileObject = open("login.json", "r")
       jsonContent = fileObject.read()
       aList = json.loads(jsonContent)
       
       self.login = int (aList['login'])
       self.Server = aList['Server'] 
       self.Password = aList['Password'] 
       self.symbol_EURUSD = aList['symbol_EURUSD'] 
       self.decimal_sambol = int (aList['decimal_sambol'] )
    
    def decimal(num , decimal_sambol):
        telo = '0.0'
        for i in range(decimal_sambol - 2):  
          telo = telo + "0"
        telo = telo + "1" 
        telo = float (telo)
        decimal_num = Decimal(str(num))
        rounded_num = decimal_num.quantize(Decimal(f'{telo}'))
        return rounded_num  

   
    def buy(symbol, lot, price , tp , deviation, magic , comment):

        return {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            # "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "comment": comment,
            "magic": magic,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK

        }

    def sell(symbol, lot, price, tp , deviation, magic, comment):

        return {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            # "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "comment": comment,
            "magic": magic,
            "type_time": mt5.ORDER_TIME_GTC,  
            "type_filling": mt5.ORDER_FILLING_FOK

        }

    def pos_buy(price_signal , shakhes , lot , symbol_EURUSD , command):

      # try:

             ask = Tick(symbol_EURUSD).ask
            #  x = Login(BUY_SELL().login, BUY_SELL().Server, BUY_SELL().Password)
            #  infologin = x.infologin(symbol_EURUSD) 
            #  ask = infologin[3]
             ask = BUY_SELL.decimal(ask , BUY_SELL().decimal_sambol)
             ask = float(ask)
             print("ask:" , ask)
             point = mt5.symbol_info(symbol_EURUSD).point
             # sl = mt5.symbol_info_tick("EURUSD").ask - 1000 * point
             tp = price_signal + shakhes * point
             
           #   filling_type = mt5.symbol_info(symbol_EURUSD).filling_mode
             request = BUY_SELL.buy(symbol_EURUSD , lot , ask , tp , 10 , 0  , command)
             result = mt5.order_send(request)
             # check the execution result
            #  print("result:" , result)
             execution = result.comment
             # position_ticket = result.order
     
             if execution == 'Request executed':
                 print("execution: buy true")


             return result    

          
      # except:
      #    print("error buy")
 
    def pos_sell(price_signal , shakhes , lot , symbol_EURUSD , command):

      # try:
        
          #  x = Login(BUY_SELL().login, BUY_SELL().Server, BUY_SELL().Password)
          #  infologin = x.infologin(symbol_EURUSD) 
          #  bid = infologin[4]

           bid = Tick(symbol_EURUSD).bid
           bid = BUY_SELL.decimal(bid , BUY_SELL().decimal_sambol)
           bid = float(bid)
           print("bid:" , bid)
   
           point = mt5.symbol_info(symbol_EURUSD).point
   
           # sl = mt5.symbol_info_tick("EURUSD").ask - 100 * point

           tp = price_signal - shakhes * point
           
           request = BUY_SELL.sell(symbol_EURUSD, lot , bid , tp , 10 , 0, command )
           result = mt5.order_send(request)
           # check the execution result
           execution = result.comment
           # position_ticket = result.order
   
           if execution == 'Request executed':
               print("execution: sell true")

           return result      

      # except:
      #   print("error sell") 

    def update_buy(symbol_EURUSD , lot , ticket , tp):
        req = {
          "action": mt5.TRADE_ACTION_SLTP,
          "symbol": symbol_EURUSD,
          "volume": lot,
          "type": mt5.ORDER_TYPE_BUY,
          "position":ticket,
          "tp": tp,
          "deviation": 10,
          "comment": "BUY_ASlah",
          "magic": 234000,
          "type_time": mt5.ORDER_TIME_GTC,
          "type_filling": mt5.ORDER_FILLING_FOK
        }
        result = mt5.order_send(req)
        execution = result.comment
             # position_ticket = result.order
     
        if execution == 'Request executed':
              print("execution: Update_buy true")
