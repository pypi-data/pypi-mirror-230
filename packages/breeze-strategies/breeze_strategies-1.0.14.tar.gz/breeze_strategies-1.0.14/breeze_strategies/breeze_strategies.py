import threading
import queue
import time 
#import datetime
import sys
import asyncio
import nest_asyncio
from breeze_connect import BreezeConnect
from datetime import datetime

#nest_asyncio.apply()

class Strategies:
    
    #initialize strategy object
    def __init__(self,app_key,secret_key,api_session,max_profit,max_loss):
        
        self.maxloss = int(max_loss)
        self.maxprofit = int(max_profit)
        self.currentcall = 0
        self.currentput = 0
        self.flag = False
        self.client = BreezeConnect(app_key)
        self.client.generate_session(secret_key,api_session)
        
        self.quantity = 0
        self.exchange_code = ""
        self.stock_code = ""
        self.product_type = ""
        self.expiry_date = ""
        self.strike_price = ""
        self.order_type = ""
        self.validity = ""
        self.stoploss = ""
        self.validity_date = ""
        self.callexecution = ""
        self.putexecution = ""
        self.strategy_type = ""
        self.socket = 0
        self.right = ""
        self.sp1_price = 0
        self.sp2_price = 0
        self.sp3_price = 0

    def squareoff(self,exchange_code, stock_code, product_type, expiry_date, strike_price, order_type, validity, stoploss, quantity, price,validity_date, trade_password, disclosed_quantity,right):
        action = "buy"
        if(self.strategy_type.lower() == "short"):
            action = "buy"
        else:
            action = "sell"

        data = self.client.square_off(exchange_code=exchange_code,
                            product="options",
                            stock_code=stock_code,
                            expiry_date=expiry_date,
                            right=right,
                            strike_price=strike_price,
                            action=action,
                            order_type=order_type,
                            validity=validity,
                            stoploss="0",
                            quantity=quantity,
                            price=price,
                            validity_date=validity_date,
                            trade_password="",
                            disclosed_quantity="0")

        print(f"Squaring off {right} ..")
        response = None
        if(data['Status'] == 200):
            response = data['Success']['message']
            print(f"Success : {response}")
        else:
            response = data['Error']
            print(f"Error : {response}")
        return(data)
        
    def get_date_format(self,expiry_date):
        month_names = {
                            '01': 'Jan',
                            '02': 'Feb',
                            '03': 'Mar',
                            '04': 'Apr',
                            '05': 'May',
                            '06': 'Jun',
                            '07': 'Jul',
                            '08': 'Aug',
                            '09': 'Sep',
                            '10': 'Oct',
                            '11': 'Nov',
                            '12': 'Dec'
                      }
        year = expiry_date[:4]
        month = expiry_date[5:7]
        day = expiry_date[8:10]
        formatted_date = f"{day}-{month_names[month]}-{year}"
        return(formatted_date)
        
    def trigger(self,product_type, rightval, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price, call_execution,put_execution,single_leg,strike_price_call, strike_price_put, is_strangle):
        net_gain_loss = (self.currentcall + self.currentput)*int(quantity)
        print(f"P&L (NET) : {round(net_gain_loss,2)}/- Rs")
        print("----------------------------------------")
        formatted_date = self.get_date_format(expiry_date)

        if(net_gain_loss > 0 and net_gain_loss >= self.maxprofit):
            print("TakeProfit reached...")
            #print("SquareOff operation on both contracts call and put begins....")
            
            if(is_strangle):
                self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price_call, right="Call", get_exchange_quotes=True, get_market_depth=False)
                self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price_put, right="Put", get_exchange_quotes=True, get_market_depth=False)
                self.stop(is_strangle)
            else:
            
                self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Call", get_exchange_quotes=True, get_market_depth=False)
                self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Put", get_exchange_quotes=True, get_market_depth=False)
                self.stop(single_leg)
            
            self.flag = True
            return
        if(net_gain_loss < 0 and net_gain_loss <= self.maxloss):
            print("MaxLoss reached...")
            #print("SquareOff operation on both contracts call and put begins....")
            
            self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Call", get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=exchange_code, stock_code=stock_code, product_type="options", expiry_date= formatted_date, strike_price=strike_price, right="Put", get_exchange_quotes=True, get_market_depth=False)
            self.stop(single_leg)
           
            self.flag = True
            return

    def calculate_current(self,product_type,stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price,put_price,call_execution,put_execution,strike_price_call, strike_price_put, is_strangle,single_leg):
        
        resultcall = []
        formatted_date = self.get_date_format(expiry_date)
        
        def on_ticks(data):
            
            value = data
            
            if(value['right'] == "Call"):
                self.currentcall = round(float(value['last']) - float(call_execution), 2)
                if(self.strategy_type.lower() == "short"):
                    self.currentcall = self.currentcall*-1
                if(self.flag == False):
                    self.trigger(product_type, "Call", stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price,put_price,call_execution,put_execution,single_leg,strike_price_call, strike_price_put, is_strangle)
            
            if(value['right'] == "Put"):
                self.currentput = round(float(value['last']) - float(put_execution), 2)
                if(self.strategy_type.lower() == "short"):
                    self.currentput = self.currentput*-1
                if(self.flag == False):
                    self.trigger(product_type, "Put", stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price,put_price,call_execution,put_execution,single_leg, strike_price_call, strike_price_put, is_strangle)
            
        self.client.on_ticks = on_ticks

        if(single_leg == False):
            self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price, right = "Call", get_exchange_quotes=True, get_market_depth=False)
            self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price, right = "Put", get_exchange_quotes=True, get_market_depth=False) 
        elif(is_strangle == True):
            self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price_call, right = "Call", get_exchange_quotes=True, get_market_depth=False)
            self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price_put, right = "Put", get_exchange_quotes=True, get_market_depth=False) 
        else:
            if(self.right.lower() == "call"):
                self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price, right = "Call", get_exchange_quotes=True, get_market_depth=False)
            else:
                self.client.subscribe_feeds(exchange_code = exchange_code, stock_code = stock_code, product_type = product_type, expiry_date= formatted_date, strike_price=strike_price, right = "Put", get_exchange_quotes=True, get_market_depth=False) 

        
    def profit_and_loss(self,product_type, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution,strike_price_call = "-1",strike_price_put = "-1",is_strangle= False,single_leg = False):
        self.calculate_current(product_type, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price, call_execution, put_execution, strike_price_call, strike_price_put, is_strangle, single_leg)
            
    def straddle(self, strategy_type,stock_code, strike_price, quantity, expiry_date, stoploss = "", put_price = "0", call_price = "0",product_type = "options", order_type = "market", validity = "day", validity_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'), exchange_code = "NFO"):
        
        self.quantity = quantity
        self.strategy_type = strategy_type
        self.exchange_code = exchange_code 
        self.stock_code = stock_code
        self.product_type = product_type 
        self.expiry_date = expiry_date  
        self.strike_price = strike_price
        self.order_type = order_type
        self.validity = validity
        self.stoploss = stoploss
        #self.quantity = quantity
        self.validity_date = validity_date
        self.flag = False
        
        if(self.socket == 0):
            self.client.ws_connect()
            self.socket = 1
            

        if(strategy_type.lower() not in ["long","short"]):
            return("strategy_type should be either long or short..")

        def place_order_method(stock_code,exchange_code,product,action,order_type,stoploss,quantity,price,validity,validity_date,expiry_date,right,strike_price,res_queue):
         
            data =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = action,
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=strike_price)
            response = None
            if(data['Status'] == 200):
                response = data['Success']['message']
                print(f"Success : {response} for {right} with order_id :{data['Success']['order_id']}")
                res_queue.put(data)
            else:
                response = data['Error']
                print(f"Error : {response} for {right}")
                res_queue.put(data)
            return(data)
                  
        res_queue = queue.Queue()
        action = "buy"

        if(strategy_type.lower()== "short"):
            action = "sell"
        
        #create thread for call and put order to execute simultaneously for buy type
        t1 = threading.Thread(target = place_order_method,args = (stock_code,exchange_code,"options",action,order_type,stoploss,quantity,call_price,validity,validity_date,expiry_date,"Call",strike_price,res_queue))
        t1.start()
        t1.join()
        
        firstresponse = res_queue.get()
        
        res_queue = queue.Queue()
        t2 = threading.Thread(target = place_order_method,args = (stock_code,exchange_code,"options",action,order_type,stoploss,quantity,put_price,validity,validity_date,expiry_date,"Put",strike_price,res_queue))
        t2.start()
        t2.join()
        secondresponse = res_queue.get()
        
        
        #if one of the order fails then cancel the other one which is successfull
        if(firstresponse.get('Status')==200 and secondresponse.get('Status')==500):
            print("Put Order Failed....")
            order_id = firstresponse['Success']['order_id']
            data  = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = order_id)

            if(data.get("Success",None) == None):
                print("Call Order Cancellation has not been successfull")
                print("----------END-------------------")
            else:
                print("Call Order Cancellation has  been successfull")
                print("----------END-------------------")
            
            
        
        elif(secondresponse.get('Status')==200 and firstresponse.get('Status')==500):
            print("Call order failed....")
            order_id = secondresponse['Success']['order_id']
            
            data = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = order_id)
            
            if(data.get("Success",None) == None):
                print("Put Order Cancellation has not been successfull")
            else:
                print("Put Order Cancellation has  been successfull")
            
        
        elif(firstresponse.get('Success',None)==None and secondresponse.get('Success',None)==None):
            print("both order call and put have failed")
            print("------------END----------------")
            
        
        else:
            orderids = [] #0th index will contain call order, #1st index will contain put order 
            orderids.append(firstresponse['Success']['order_id']) 
            orderids.append(secondresponse['Success']['order_id'])            
            #define a mechanism to get profit and loss
            print("\n")
            print("----Starting live P&L feed...---")
            time.sleep(5)
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= orderids[0])

            call_status = None
            put_status = None

            #print(details)
            call_execution = -1
            put_execution = -1
            
            #print(f"order ids are : {orderids}")
            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    call_execution = entry['average_price']
                    call_status = "Executed"
                    self.callexecution = call_execution
                    break
                    
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= orderids[1])
            #print(details)
            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    put_execution = entry['average_price']
                    put_status = "Executed"
                    self.putexecution = put_execution
                    break
                    
            if(call_execution == -1 or put_execution == -1):
                print("Dear User order could not execute within time limit ..cancelling it")
                
                
                if(call_execution == -1 and put_execution == -1):
                    print("Both Order Call and Put could not execute to so cancelling it ..... ")
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[0])
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[1])

                elif(call_execution == -1):
                    #call cancel order api
                    print("call order could not execute due to some reason so cancelling order")
                    #self.squareoff(self,rightval,exchange_code, stock_code, product_type, expiry_date, right, strike_price, action, order_type, validity, stoploss, quantity, price,validity_date, trade_password, disclosed_quantity)
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[0])

                    print("put order is executed squaring off....")
                    
                    self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")

                elif(put_execution == -1):
                    #call cancel order api
                    print("put order could not execute due to some reason so cancelling order")
                    status = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[1])
                    print("call order is executed squaring off....")
                    self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
                    
            else:
                print("Call order got executed at price :{0} Rs and Put Order got executed at price : {1} Rs".format(call_execution,put_execution))
                self.profit_and_loss(product_type, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution)
            
    
    
    
    def stop(self,single_leg = False,is_butterfly = False,is_strangle = False):
        if(self.socket == 1):
            self.client.ws_disconnect()
        self.socket = 0
        time.sleep(1)
        print("\n")
        print("Squaring off the  contracts and exiting strategy...")
        print("----------------------------------------")
        if(is_butterfly == True):
            square1 = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = sp1 , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = self.right)
            square2 = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = sp2 , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = self.right)
            square3 = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = sp3 , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = self.right)
            self.report(square1,square2,square3)
        elif(is_strangle == True):
            square_call = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price_call , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
            square_put = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price_put , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")
            print("----------------------------------------")
            self.create_report(square_call,square_put,single_leg)
        elif(is_butterfly == False and single_leg == False):

            square_call = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
            square_put = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")
            print("----------------------------------------")
            self.create_report(square_call,square_put,single_leg)
        else:

            if(self.right.lower() == "call"):
                square_call = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
                print("----------------------------------------")
                self.create_report(square_call,None,single_leg)
            else:
                square_put = self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = self.strike_price , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")
                print("----------------------------------------")
                self.create_report(None,square_put,single_leg)


    def get_pnl(self,is_butterfly = False):
        if(is_butterfly == True):
            outcome = (self.sp1_price + self.sp2_price + self.sp3_price)*int(quantity)
            print(f"P&L (NET) : {round(outcome,2)}/- Rs")
        else:
            outcome = (self.currentcall + self.currentput)*int(self.quantity)
            print(f"P&L (NET) : {round(outcome,2)}/- Rs")

        print("----------------------------------------")

    def report(self,square1,square2,square3):
        if(square1['Status'] == 200 and square2['Status'] == 200 and square3['Status'] == 200):
            sq1_id = square1['Status']['order_id']
            sq2_id = square2['Status']['order_id']
            sq3_id = square3['Status']['order_id']
            print("\nGenerating Final P&L report in 5 seconds....")
            time.sleep(5)
            
            records = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq1_id)
            
            sq1_price = -1
            
            for record in records['Success']:
                if(record['status'] == "Executed"):
                    sq1_price = record["average_price"]
                    break
                
                
            records = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq2_id)
            
            sq2_price = -1
            
            for record in records['Success']:
                if(record['status'] == "Executed"):
                    sq2_price = record["average_price"]
                    break
            
            records = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq3_id)
            
            sq3_price = -1
            
            for record in records['Success']:
                if(record['status'] == "Executed"):
                    sq3_price = record["average_price"]
                    break
                
            p1 = round((float(sq1_price) - float(self.exec1))*int(self.quantity),2) # calculate p & l
            p2 = round((float(sq2_price) - float(self.exec2))*int(self.quantity),2) # calculate p & l
            p3 = round((float(sq3_price) - float(self.exec3))*int(self.quantity),2) # calculate p & l
            
            
            print("----------------------------------------")
            print("Profit and Loss Report........")
            print(f"P&L ({self.sp1}) : {p1}/- Rs")
            print(f"P&L ({self.sp2}) : {p2}/- Rs")
            print(f"P&L ({self.sp3}) : {p3}/- Rs")
            print(f"P&L (NET) : {p1 + p2 + p3}/- Rs")
            
    def create_report(self,sq_call,sq_put,single_leg):

        if(single_leg):
            if(self.right.lower() == "call"):
                if(sq_call['Status'] == 200):
                    sq_callid = sq_call["Success"]['order_id']
                    print("\nGenerating Final P&L report in 5 seconds....")
                    time.sleep(5)
                    callrecords = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq_callid)

                    sqcall_price = -1
                    for record in callrecords['Success']:
                        if(record['status'] == "Executed"):
                            sqcall_price = record["average_price"]
                            break
                    
                    plcall = round((float(sqcall_price) - float(self.callexecution))*int(self.quantity),2)
                    self.currentcall = (float(sqcall_price) - float(self.callexecution))

                    print("----------------------------------------")
                    print("Profit and Loss Report........")
                    print(f"P&L (CALL) : {plcall}/- Rs")
                    
                    print(f"P&L (NET) : {plcall}/- Rs")
                    print("----------------------------------------")
                
                else:
                    print("Error : SquareOff for call operation failed.")
            
            else:
                if(sq_put['Status'] == 200):
                    sq_putid = sq_put["Success"]['order_id']
                    print("\nGenerating Final P&L report in 5 seconds....")
                    time.sleep(5)
                    putrecords = self.client.get_order_detail(exchange_code=self.exchange_code,
                    order_id= sq_putid)

                    sqput_price = -1
                    for record in putrecords['Success']:
                        if(record['status'] == "Executed"):
                            sqput_price = record["average_price"]
                            break
                    
                    plput = round((float(sqput_price) - float(self.putexecution))*int(self.quantity),2)
                    self.currentput = (float(sqput_price) - float(self.putexecution))

                    print("----------------------------------------")
                    print("Profit and Loss Report........")
                    
                    print(f"P&L (PUT) : {plput}/- Rs")
                    print(f"P&L (NET) : {plput}/- Rs")
                    print("----------------------------------------")
                
                else:
                    print("Error : SquareOff for put operation failed.")

            return
        
        if(sq_call['Status'] == 200 and sq_put['Status'] == 200):
            sq_callid = sq_call["Success"]['order_id']
            sq_putid = sq_put["Success"]['order_id']

            print("\nGenerating Final P&L report in 5 seconds....")
            time.sleep(5)
            callrecords = self.client.get_order_detail(exchange_code=self.exchange_code,
                        order_id= sq_callid)

            putrecords = self.client.get_order_detail(exchange_code=self.exchange_code,
                        order_id= sq_putid)

            sqcall_price = -1
            sqput_price = -1
            #time.sleep(5)
            for record in callrecords['Success']:
                if(record['status'] == "Executed"):
                    sqcall_price = record["average_price"]
                    break
            for record in putrecords["Success"]:
                if(record['status'] == "Executed"):
                    sqput_price = record["average_price"]
                    break
            
            plcall = round((float(sqcall_price) - float(self.callexecution))*int(self.quantity),2)
            plput = round((float(sqput_price) - float(self.putexecution))*int(self.quantity),2)

            self.currentcall = (float(sqcall_price) - float(self.callexecution))
            self.currentput = (float(sqput_price) - float(self.putexecution))

            print("----------------------------------------")
            print("Profit and Loss Report........")
            print(f"P&L (CALL) : {plcall}/- Rs")
            print(f"P&L (PUT) : {plput}/- Rs")
            print(f"P&L (NET) : {plput + plcall}/- Rs")
            print("----------------------------------------")
        else:
            print("One of Square off operation failed..")


    def single_leg(self,right, strategy_type,stock_code, strike_price, quantity, expiry_date, price = "0", stoploss = "",product_type = "options", order_type = "market", validity = "day", validity_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'), exchange_code = "NFO",put_price = "0", call_price = "0"):
        self.quantity = quantity
        self.strategy_type = strategy_type
        self.exchange_code = exchange_code 
        self.stock_code = stock_code
        self.product_type = product_type 
        self.expiry_date = expiry_date  
        self.strike_price = strike_price
        self.order_type = order_type
        self.validity = validity
        self.stoploss = stoploss
        #self.quantity = quantity
        self.validity_date = validity_date
        self.right = right
        self.flag = False

        if(self.socket == 0):
            self.client.ws_connect()
            self.socket = 1

        action = "buy"

        if(self.strategy_type.lower() == "short"):
            action = "sell"


        data =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = action,
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=strike_price)

        response = None
        order_id = None
        if(data['Status'] == 200):
            response = data['Success']['message']
            print(f"Success : {response} for {right} with order_id :{data['Success']['order_id']}") 
            order_id = data['Success']['order_id']      
        
        else:
            response = data['Error']
            print(f"Error : {response} for {right}")

        if(order_id!=None):
            print("\n")
            print("----Starting live P&L feed...---")
            time.sleep(5)
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= order_id)

            #execution_price = -1
            
            
            #print(f"order ids are : {orderids}")
            call_execution = "0"
            put_execution = "0"

            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    execution = entry['average_price']
                    #call_status = "Executed"
                    if(right.lower() == "call"):
                        call_execution = execution
                        self.callexecution = execution
                        break
                    else:
                        put_execution = execution
                        self.putexecution = execution
                        break

        self.profit_and_loss(product_type, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution,True)

    
    def checklimit(self,sp1,sp2,sp3):
        self.sp1 = sp1
        self.sp2 = sp2
        self.sp3 = sp3
        
        net_gain_loss = (self.sp1_price + self.sp2_price + self.sp3_price)*int(quantity)
        print(f"P&L (NET) : {round(net_gain_loss,2)}/- Rs")
        print("----------------------------------------")
        formatted_date = self.get_date_format(self.expiry_date)

        if(net_gain_loss > 0 and net_gain_loss >= self.maxprofit):
            print("TakeProfit reached...")
            #print("SquareOff operation on both contracts call and put begins....")
            
            
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp1, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp2, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp3, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.stop(is_butterfly = True)
            
            #self.flag = True
            return
        if(net_gain_loss < 0 and net_gain_loss <= self.maxloss):
            print("MaxLoss reached...")
            #print("SquareOff operation on both contracts call and put begins....")
            
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp1, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp2, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.client.unsubscribe_feeds(exchange_code=self.exchange_code, stock_code = self.stock_code, product_type="options", expiry_date= formatted_date, strike_price=sp3, right=self.right, get_exchange_quotes=True, get_market_depth=False)
            self.stop(is_butterfly = True)
            return
        
    def monitor_pnl(self,exec1,exec2,exec3,sp1,sp2,sp3):
        self.exec1 = exec1
        self.exec2 = exec2
        self.exec3 = exec3
        formatted_date = self.get_date_format(self.expiry_date)
        def on_ticks(data):
            value = data
            if(value['strike_price'] == sp1):
                self.sp1_price = round(float(value['last']) - float(exec1), 2)
                if(self.strategy_type.lower() == "short"):
                    self.sp1_price = self.sp1_price*-1
                    
                self.checklimit(sp1,sp2,sp3)
                    
            if(value['strike_price'] == sp2):
                self.sp2_price = round(float(value['last']) - float(exec2), 2)
                if(self.strategy_type.lower() == "short"):
                    self.sp2_price = self.sp2_price*-1
                self.checklimit(sp1,sp2,sp3)
                
            if(value['strike_price'] == sp3):
                self.sp3_price = round(float(value['last']) - float(exec3), 2)
                if(self.strategy_type.lower() == "short"):
                    self.sp3_price = self.sp3_price*-1
                self.checklimit(sp1,sp2,sp3)
                
        self.client.on_ticks = on_ticks
        self.client.subscribe_feeds(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = "options", expiry_date= formatted_date, strike_price=sp1, right = self.right, get_exchange_quotes=True, get_market_depth=False) 
        self.client.subscribe_feeds(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = "options", expiry_date= formatted_date, strike_price=sp2, right = self.right, get_exchange_quotes=True, get_market_depth=False) 
        self.client.subscribe_feeds(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = "options", expiry_date= formatted_date, strike_price=sp3, right = self.right, get_exchange_quotes=True, get_market_depth=False) 

    
    def butterfly(self,right,strategy_type,stock_code,spread, strike_price, quantity, expiry_date, stoploss = "",product_type = "options", order_type = "market", validity = "day", validity_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'), exchange_code = "NFO"):
        self.strategy_type = strategy_type
        self.right = right
        self.quantity = quantity
        self.expiry_date = expiry_date
        self.exchange_code = exchange_code
        self.validity_date = validity_date
        self.strike_price = strike_price
        self.order_type = order_type
        self.stoploss = stoploss
        self.validity = validity

        if(self.socket == 0):
            self.client.ws_connect()
            self.socket = 1
            
        
        action = "sell"
        alternate = dict()
        
        alternate["buy"] = "sell"
        alternate["sell"] = "buy"
        
        
        if(strategy_type.lower() == "short"):
            action = "buy"
        
        data =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = action,
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=strike_price)
        
        sprice1 = str(float(strike_price) - float(spread))
        sprice2 = str(float(strike_price) + float(spread))

        data2 =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = alternate[action],
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=sprice1)
        
        data3 =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = alternate[action],
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity = quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right = right,
                    strike_price=sprice2)
        order_ids = []
        
        if(data['Status'] == 200):
            response = data['Success']['message']
            print(f"Success : {response} for {right} with order_id :{data['Success']['order_id']}") 
            order_id = data['Success']['order_id']      
            order_ids.append(order_id)
            
        else:
            response = data['Error']
            print(f"Error : {response} for {right}")
            
        if(data2['Status'] == 200):
            response = data2['Success']['message']
            print(f"Success : {response} for {right} with order_id :{data2['Success']['order_id']}") 
            order_id = data2['Success']['order_id']      
            order_ids.append(order_id)
        else:
            response = data2['Error']
            print(f"Error : {response} for {right}")


        if(data3['Status'] == 200):
            response = data3['Success']['message']
            print(f"Success : {response} for {right} with order_id :{data3['Success']['order_id']}") 
            order_id = data3['Success']['order_id']     
            order_ids.append(order_id)
            
        else:
            response = data3['Error']
            print(f"Error : {response} for {right}")
        
        time.sleep(5)
        
        execution1 ="0" #first order
        execution2  ="0" # second order
        execution3 ="0" # third order
        
        if(len(order_ids) == 3):
            res1 = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= order_ids[0])
            res2 = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= order_ids[1])
            res3 = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= order_ids[2])
            

            for entry in res1['Success']:
                if(entry['status'] == "Executed"):
                    execution1 = entry['average_price']
                    break
            
            for entry in res2['Success']:
                if(entry['status'] == "Executed"):
                    execution2 = entry['average_price']
                    break
            
            for entry in res3['Success']:
                if(entry['status'] == "Executed"):
                    execution3 = entry['average_price']
                    break
            monitor_pnl(execution1,execution2,execution3,sprice1,strike_price,sprice2)
    
    # implementation of strangle       
    def strangle(self,strike_price_call,strike_price_put, strategy_type,stock_code, quantity, expiry_date, stoploss = "", put_price = "0", call_price = "0",product_type = "options", order_type = "market", validity = "day", validity_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'), exchange_code = "NFO"):
        self.quantity = quantity
        self.strategy_type = strategy_type
        self.exchange_code = exchange_code 
        self.stock_code = stock_code
        self.product_type = product_type 
        self.expiry_date = expiry_date  
        #self.strike_price = strike_price
        self.order_type = order_type
        self.validity = validity
        self.stoploss = stoploss
        self.validity_date = validity_date
        self.strike_price_call = strike_price_call
        self.strike_price_put = strike_price_put
        self.flag = False
        
        if(self.socket == 0):
            self.client.ws_connect()
            self.socket = 1
            

        if(strategy_type.lower() not in ["long","short"]):
            return("strategy_type should be either long or short..")

        def place_order_method(stock_code,exchange_code,product,action,order_type,stoploss,quantity,price,validity,validity_date,expiry_date,right,strike_price,res_queue):
         
            data =  self.client.place_order(stock_code=stock_code,
                    exchange_code=exchange_code,
                    product="options",
                    action = action,
                    order_type=order_type,
                    stoploss=stoploss,
                    quantity=quantity,
                    price = price,
                    validity= validity,
                    validity_date = validity_date,
                    disclosed_quantity = "0",
                    expiry_date = expiry_date,
                    right= right,
                    strike_price=strike_price)
            response = None
            if(data['Status'] == 200):
                response = data['Success']['message']
                print(f"Success : {response} for {right} with order_id :{data['Success']['order_id']}")
                res_queue.put(data)
            else:
                response = data['Error']
                print(f"Error : {response} for {right}")
                res_queue.put(data)
            return(data)
                  
        res_queue = queue.Queue()
        action = "buy"

        if(strategy_type.lower()== "short"):
            action = "sell"
        
        #create thread for call and put order to execute simultaneously for buy type
        t1 = threading.Thread(target = place_order_method,args = (stock_code,exchange_code,"options",action,order_type,stoploss,quantity,call_price,validity,validity_date,expiry_date,"Call",strike_price_call,res_queue))
        t1.start()
        t1.join()
        
        firstresponse = res_queue.get()
        
        res_queue = queue.Queue()
        t2 = threading.Thread(target = place_order_method,args = (stock_code,exchange_code,"options",action,order_type,stoploss,quantity,put_price,validity,validity_date,expiry_date,"Put",strike_price_put,res_queue))
        t2.start()
        t2.join()
        secondresponse = res_queue.get()
        
        
        #if one of the order fails then cancel the other one which is successfull
        if(firstresponse.get('Status')==200 and secondresponse.get('Status')==500):
            print("Put Order Failed....")
            order_id = firstresponse['Success']['order_id']
            data  = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = order_id)

            if(data.get("Success",None) == None):
                print("Call Order Cancellation has not been successfull")
                print("----------END-------------------")
            else:
                print("Call Order Cancellation has  been successfull")
                print("----------END-------------------")
            
            
        
        elif(secondresponse.get('Status')==200 and firstresponse.get('Status')==500):
            print("Call order failed....")
            order_id = secondresponse['Success']['order_id']
            
            data = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = order_id)
            
            if(data.get("Success",None) == None):
                print("Put Order Cancellation has not been successfull")
            else:
                print("Put Order Cancellation has  been successfull")
            
        
        elif(firstresponse.get('Success',None)==None and secondresponse.get('Success',None)==None):
            print("both order call and put have failed")
            print("------------END----------------")
            
        
        else:
            orderids = [] #0th index will contain call order, #1st index will contain put order 
            orderids.append(firstresponse['Success']['order_id']) 
            orderids.append(secondresponse['Success']['order_id'])            
            #define a mechanism to get profit and loss
            print("\n")
            print("----Starting live P&L feed...---")
            time.sleep(5)
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= orderids[0])

            call_status = None
            put_status = None

            #print(details)
            call_execution = -1
            put_execution = -1
            
            #print(f"order ids are : {orderids}")
            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    call_execution = entry['average_price']
                    call_status = "Executed"
                    self.callexecution = call_execution
                    break
                    
            details = self.client.get_order_detail(exchange_code=exchange_code,
                        order_id= orderids[1])
            #print(details)
            for entry in details['Success']:
                if(entry['status'] == "Executed"):
                    put_execution = entry['average_price']
                    put_status = "Executed"
                    self.putexecution = put_execution
                    break
                    
            if(call_execution == -1 or put_execution == -1):
                print("Dear User order could not execute within time limit ..cancelling it")
                
                
                if(call_execution == -1 and put_execution == -1):
                    print("Both Order Call and Put could not execute to so cancelling it ..... ")
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[0])
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[1])

                elif(call_execution == -1):
                    #call cancel order api
                    print("call order could not execute due to some reason so cancelling order")
                    #self.squareoff(self,rightval,exchange_code, stock_code, product_type, expiry_date, right, strike_price, action, order_type, validity, stoploss, quantity, price,validity_date, trade_password, disclosed_quantity)
                    self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[0])

                    print("put order is executed squaring off....")
                    
                    self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = strike_price_put , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Put")

                elif(put_execution == -1):
                    #call cancel order api
                    print("put order could not execute due to some reason so cancelling order")
                    status = self.client.cancel_order(exchange_code=exchange_code,
                    order_id = orderids[1])
                    print("call order is executed squaring off....")
                    self.squareoff(exchange_code = self.exchange_code, stock_code = self.stock_code, product_type = self.product_type , expiry_date = self.expiry_date , strike_price = strike_price_call , order_type = self.order_type, validity = self.validity, stoploss = self.stoploss, quantity = self.quantity, price = "", validity_date = self.validity_date, trade_password = "", disclosed_quantity="0",right = "Call")
                    
            else:
                print("Call order got executed at price :{0} Rs and Put Order got executed at price : {1} Rs".format(call_execution,put_execution))
                self.profit_and_loss(product_type, stock_code, strike_price, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution,strike_price_call,strike_price_put,is_strangle = True)
                #self.profit_and_loss(product_type, stock_code, strike_price_put, quantity, expiry_date, order_type, validity, validity_date, exchange_code, stoploss, call_price, put_price,call_execution,put_execution)
