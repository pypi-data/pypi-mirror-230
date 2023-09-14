import json
import sqlite3
import MetaTrader5 as mt5
import pandas as pd


from login_forex_next3 import Login
from timecandel_pos_forex_next3 import Timecandel
from database_ex_forex_next3 import Database
from tick_ex_forex_next3 import Tick  
from decimal import Decimal
  
class LINE:
   
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

   def point_line(p2 , p3 , p4 , t2 , t3 , t4 , tn ):

      # print ("p2:" , p2)
      # print ("p3:" , p3)
      # print ("p4:" , p4)
      p = ((p2-p4) / (t2-t4)) * tn + p3 - ((p2-p4)/(t2-t4)) * t3
      # print ("p:" , p)
      p = LINE.decimal(p , LINE().decimal_sambol)
      pp = float(p)
      # print ("pp:" , pp)
      return pp
   
   def cal_point_line(candel_num  , tn):
        
        lab = Database.select_table_One(candel_num)

        price_close = lab[0][9]
        timepstamp = lab[0][19]

        # print("timepstamp:" , timepstamp)

        price_close = json.loads(price_close)
        timepstamp = json.loads(timepstamp)

        t2 = int (timepstamp[1])
        t3 = int (timepstamp[2]) + 840
        t4 = int (timepstamp[3])
        
        p2 = float (price_close[1]) 
        p3 = float (price_close[2])
        p4 = float (price_close[3])

        # print("t2:" , t2)
        # print("t3:" , t3)
        # print("t4:" , t4)
        # print("tn:" , tn)

        # print("p2:" , p2)
        # print("p3:" , p3)
        # print("p4:" , p4)

        line_DB = LINE.point_line(p2 , p3 , p4 , t2 , t3 , t4 , tn )
        # print("line_DB:" , line_DB)

        return line_DB
          
   def line_run(candel_num , symbol_EURUSD , tn ):
      
      try:

        lab = Database.select_table_One(candel_num)
        # print("lab:" , lab[0])
        point_patern = lab[0][3]
        gap_point = lab[0][10]
        gap_amount = lab[0][11]
        price_close = lab[0][9]
        price_open = lab[0][8]
        timepstamp = lab[0][19]
        
        # print("point_patern:" , point_patern)
      #   print("gap_point:" , gap_point)
        # print("gap_amount:" , gap_amount)
        # print("price_close:" , price_close)
        
        gap_point = json.loads(gap_point)
        point_patern = json.loads(point_patern)
        price_close = json.loads(price_close)
        gap_amount = json.loads(gap_amount)
        price_open = json.loads(price_open)
        timepstamp = json.loads(timepstamp)

      #   time_point_start = timepstamp[2]
      # #   print("time_point_start:" , time_point_start)
      #   time_point_start = int(time_point_start) + 840
      #   # print("time_point_start:" , time_point_start)
        
      #   timecandel_mine = mt5.copy_rates_from(symbol_EURUSD, mt5.TIMEFRAME_M1, time_point_start , 1)
      # #   print("timecandel_mine:" , timecandel_mine)

      #   point_start = timecandel_mine[0][4]
      #   point_start = LINE.decimal(point_start , LINE().decimal_sambol)
      #   point_start = float(point_start)

      #   timecandel_mine_gap = mt5.copy_rates_from(symbol_EURUSD, mt5.TIMEFRAME_M1, time_point_start + 60 , 1)

      #   point_start_gap = timecandel_mine_gap [0][1]
                

      #   print("point_start:" , point_start)
      #   print("gap_amount:" , gap_amount)
        
        list_point_gap = []
        list_point_gap_point3 = []
        list_point_gap_total = []
        
        p = 0
        p22 = 0
        p33 = 0
        p44 = 0

        gaps = False
        point_patern_gap3 = 0


        len_point = len (gap_point)

        x1 = x2 = x3 = 0
        for index in range(len_point):
               
             try:  
               if index == 0:
                 x1 = gap_point[index]
                #  print("x1:" , x1)
                 
                 if x1 == 2:
                       p22 = gap_amount[index]

                 elif x1 == 3:
                       p33 = gap_amount[index]

                 elif x1 == 4:
                       p44 = gap_amount[index]      
                             
               elif index == 1: 
                 x2 = gap_point[index]
                #  print("x2:" , x2)
                 if x2 == 2:
                       p22 = gap_amount[index]

                 elif x2 == 3:
                       p33 = gap_amount[index]

                 elif x2 == 4:
                       p44 = gap_amount[index]
                 
               elif index == 2:  
                 x3 = gap_point[index]
                 if x3 == 2:
                       p22 = gap_amount[index]

                 elif x3 == 3:
                       p33 = gap_amount[index]

                 elif x3 == 4:
                       p44 = gap_amount[index]
                #  print("x3:" , x3)
             except:
                  break    

       
        tn = tn
        # print("t3:" ,timepstamp[2])

        t2 = int (timepstamp[1]) 
        t3 = int (timepstamp[2]) + 840 + 59
        t4 = int (timepstamp[3]) 
        
        p2 = float (price_close[1]) 
        p3 = float (price_close[2])
        p4 = float (price_close[3])

        # print("t2:" , t2)
        # print("t3:" , t3)
        # print("t4:" , t4)
        # print("tn:" , tn)

        # print("p22:" , p22)
        # print("p33:" , p33)
        # print("p44:" , p44)

        # print("p2:" , p2)
        # print("p3:" , p3)
        # print("p4:" , p4)

        list_line = []
        
        
        for index in range(1):
           
               if p == 0:
                        line_DB = LINE.point_line(p2 , p3 , p4 , t2 , t3 , t4 , tn )
                        line_DB = float(line_DB)
                        list_point_gap.append(line_DB)
                        list_point_gap_total.append(line_DB)
                        list_line.append("Line_p")
                        
        
               if p22 != 0:
                        line_DB = LINE.point_line(p22 , p3 , p4 , t2 , t3 , t4 , tn )
                        line_DB = float(line_DB)
                        list_point_gap.append(line_DB)  
                        list_point_gap_total.append(line_DB)
                        list_line.append("Line_p22")
        
               if p33 != 0:
                        line_DB = LINE.point_line(p2 , p33 , p4 , t2 , t3 , t4 , tn )
                        line_DB = float(line_DB)
                        list_point_gap_point3.append(line_DB) 
                        list_point_gap_total.append(line_DB)
                        list_line.append("Line_p33")
                        gaps = True
        
               if p44 != 0:
                        line_DB = LINE.point_line(p2 , p3 , p44 , t2 , t3 , t4 , tn)
                        line_DB = float(line_DB)
                        list_point_gap.append(line_DB)   
                        list_point_gap_total.append(line_DB) 
                        list_line.append("Line_p44")
        
               if p22 != 0 and p33!=0:
                        line_DB = LINE.point_line(p22 , p33 , p4 , t2 , t3 , t4 , tn)
                        line_DB = float(line_DB)
                        list_point_gap_point3.append(line_DB)  
                        list_point_gap_total.append(line_DB)
                        list_line.append("Line_p22_p33")
                        gaps = True
        
               if p33 != 0 and p44!=0:
                        line_DB = LINE.point_line(p2 , p33 , p44 , t2 , t3 , t4 , tn )
                        line_DB = float(line_DB)
                        list_point_gap_point3.append(line_DB) 
                        list_point_gap_total.append(line_DB)
                        list_line.append("Line_p33_p44")
                        gaps = True
        
               if p22 != 0 and p44!=0:
                        line_DB = LINE.point_line(p22 , p3 , p44 , t2 , t3 , t4 , tn)
                        line_DB = float(line_DB)
                        list_point_gap.append(line_DB)  
                        list_point_gap_total.append(line_DB)  
                        list_line.append("Line_p22_p44")              
        
               if p22 != 0 and p33 != 0 and p44 != 0:
                        line_DB = LINE.point_line(p22 , p33 , p44 , t2 , t3 , t4 , tn )
                        line_DB = float(line_DB)
                        list_point_gap_point3.append(line_DB)
                        list_point_gap_total.append(line_DB)
                        list_line.append("Line_p22_p33_p44")
                        gaps = True
        

        # if gaps == True:
        #         io = point_start
        #         io = io + 1
                # point_patern_gap3 = timecandel_360[io][1]
                # timepstamp_point_start = timecandel_360[point_start][0]

      #   print("list_point_gap:" , list_point_gap)
      #   print("list_point_gap_point3:" , list_point_gap_point3)
      #   print("point_patern_gap3:" , point_patern_gap3)
        # print("list_point_gap_total:" , list_point_gap_total)

        # print("list_Line" , list_line)
        
        timecandel_mine360 = mt5.copy_rates_from(symbol_EURUSD, mt5.TIMEFRAME_M1, tn , 361)
        # Show2(timecandel_mine360 , point_start , time_point_start , point_start_gap , list_point_gap , list_point_gap_point3 , gaps )

        return [list_point_gap_total , list_line ]
      except sqlite3.Error as error:
               print("Failed to line_run", error)  

   def line_shakhes(candel_num , symbol_EURUSD , decimal_sambol):
     
        lab = Database.select_table_One(candel_num)

        point_close = lab[0][9]
        timepstamp = lab[0][19]
        point_close = json.loads(point_close)
        timepstamp = json.loads(timepstamp)

        # print("point_close:" , point_close)
        # print("timepstamp:" , timepstamp)
        
        timepstamp_3 = int (timepstamp[3]) + 840
        price_close_3 = float(point_close[3])

        # print("price_close_3:" , price_close_3)

        line_point = LINE.cal_point_line(candel_num , timepstamp_3)
        line_point = float(line_point)
        # print("input:" , line_point)
        rec = Timecandel.time_candel_timestamp(symbol_EURUSD , timepstamp_3)
        timecandel = rec[0]
        # Show(timecandel  , 21 , [line_point])

        x = 10
        for i in range(decimal_sambol):
            x = x * 10

        price_close_3 = price_close_3 * x
        line_point = line_point * x

        price_close_3 = int (price_close_3)
        line_point = int (line_point)

        # print("price_close_3:" , price_close_3)
        # print("line_point:" , line_point)


        amount_shakhes = abs (price_close_3 - line_point)
        amount_shakhes = amount_shakhes / 10
        amount_shakhes = int(amount_shakhes)

        # print("amount_shakhes:" , amount_shakhes)


        # x = Login(LINE().login, LINE().Server, LINE().Password)

        # aaa = Login.auth()
        # print("aaaa:" , aaa)

        # infologin = x.infologin(symbol_EURUSD) 
        # print('infologin' , infologin)
        ask = Tick(symbol_EURUSD).ask
        bid = Tick(symbol_EURUSD).bid

        # ask = infologin[3]
        # bid = infologin[4]

        # print("ask:" , ask)
        # print("bid:" , bid)

        x = 10
        for i in range(decimal_sambol):
            x = x * 10

        a = ask * x
        b = bid * x

        a = int (a)
        b = int (b)

        sprade = a - b

        sprade = int (sprade)
        sprade = sprade /10
        sprade = int (sprade)
        print("sprade:" , sprade)

        
        if amount_shakhes > (sprade * 2):
            
           return [amount_shakhes , True]
        
        else:
             
           return [amount_shakhes , False]  





