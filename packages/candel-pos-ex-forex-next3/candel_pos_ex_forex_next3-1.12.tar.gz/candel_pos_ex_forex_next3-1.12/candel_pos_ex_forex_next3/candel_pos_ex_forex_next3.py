import json
from database_ex_forex_next3 import Database
import pandas as pd
import MetaTrader5 as mt5

class Candel:

    def timecandel(symbol , timestamp ):
    # def timecandel(symbol):
      try:
          timecandel = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M15, timestamp, 25)
        #   timecandel = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 25)
        #   timecandel = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 24)

          return timecandel
      except:
          return False
      
    def candelstate(x , listOpen , listClose):
         candel_open = listOpen[x]
         candel_close = listClose[x]
        #  candel_open = Candel.decimal(candel_open)
        #  candel_close = Candel.decimal(candel_close)
        #  print("candel_open" , candel_open) 
        #  print("candel_close" , candel_close) 
         if candel_open > candel_close:
             candel_state = "red"
     
         elif candel_open < candel_close:
             candel_state = "green"
                 
         elif candel_open == candel_close:
             candel_state = "doji"
     
         return candel_state     

class Candel_pos:
    
   def candel_red (listOpen , listClose , listTimestamp):

       candel = []
       EP1 = []
       x = 0
       candel_num = 0
       original_range = range(0, 24)
       reversed_range = list(original_range)[::-1]
    #    print("reversed_range:" , reversed_range)
       for num in reversed_range:
        
                   candel_state = Candel.candelstate(num , listOpen , listClose)  
                #    print("i:" , num) 
       
                   
                #    print("candel0: " + f'{candel_state}') 
                   candel.append(candel_state)
                   if candel_state == "red": 
                        x_node = 23 - num
                        EP1.append(num + x_node)
                        EP1.append(num)
                        original_range = range(0, num)
                        reversed_range2 = list(original_range)[::-1]
                        # print("reversed_range2:" , reversed_range2)
                        for i2 in reversed_range2 :  
                            candel_state = Candel.candelstate(i2 , listOpen , listClose) 
                            # print("i2:" , i2)    
                            # print("candel1: " + f'{candel_state}')
                            candel.append(candel_state)
                            if candel_state == "green":
                             
                              original_range = range(0, i2)
                              reversed_range3 = list(original_range)[::-1]
                            #   print("reversed_range3:" , reversed_range3)
                              for i3 in reversed_range3:  
                                   candel_state = Candel.candelstate(i3 , listOpen , listClose)   
                                #    print("i3:" , i3)   
                                #    print("candel2: " + f'{candel_state}')
                                   candel.append(candel_state)
                                   if candel_state == "red":
                                      x_node = i2 - i3
                                      EP1.append(i3 + x_node)
                                      EP1.append(i3)
                                      print("the end")
                                      x = 1
                                      break
       
                                   if x == 1:
                                     break    
                                      
                            if x == 1:
                                  break  
                   if x == 1:
                         break    

       prices_candel_close = []
       prices_candel_open = []
       time_candel = []
       times = []
        
       for index in EP1: 
            prices_candel_close.append(listClose[index])
            prices_candel_open.append(listOpen[index])
            time_candel.append(str (listTimestamp[index]))
            times.append(str (pd.to_datetime( listTimestamp[index] , unit='s')))                   
       
              
      #  print ("candel:" , candel)
       EP1.reverse()
       candel.reverse()
       prices_candel_close.reverse()
       prices_candel_open.reverse()
       time_candel.reverse()
       times.reverse()
      #  print ("EP:" , EP1)
      #  print ("candel:" , candel)

       list_len = len(EP1)
      #  print("list_len:" , list_len)

       
       try:
         select_all = Database.select_table_All()
         # print("select_all:" , select_all)
         if select_all == []:
          candel_num = 1 
         else:
              
              select_all_len = len(select_all)
              print("select_all_len:" , select_all_len)
              rec = select_all[select_all_len - 1]
              print("select_all:" , rec)
              candel_num = int (rec[1])
              print("rec:" , rec)
              candel_num = candel_num + 1
              print("candel_num:" , candel_num)

       except:
          print("erooooor select_all")

       if list_len == 4 and x == 1  :
            end = EP1[0]
            point = EP1[3]
            print("end:" , end)
            time_end_patterns =  listTimestamp [end]  
            time_start_patern = listTimestamp [point]
            # print("time_end_pattern:" , time_end_pattern)
            time_end_pattern = time_end_patterns + 21600
            # print("time_end_pattern:" , time_end_pattern)
            time_start_patern = time_start_patern + 1800
            # print("time_start_pattern:" , time_start_patern)

            EP1 = json.dumps(EP1)
            candel = json.dumps(candel)
            prices_candel_close = json.dumps(prices_candel_close)
            prices_candel_open = json.dumps(prices_candel_open)
            time_candel = json.dumps(time_candel)
            times = json.dumps(times)
            value = (candel_num , "Two_TOP" , EP1 , "" , "" , "" , candel , prices_candel_open ,prices_candel_close , "" , "" , "" , "" , "false", "true" , "false" , time_start_patern , time_end_pattern ,time_candel , times , "" , "" , "" )
            Database.insert_table(value)
          

   def candel_green (listOpen , listClose , listTimestamp):

       candel = []
       EP1 = []
       x = 0
       candel_num = 0
       original_range = range(0, 24)
       reversed_range = list(original_range)[::-1]
    #    print("reversed_range:" , reversed_range)
       for num in reversed_range:
         
                   candel_state = Candel.candelstate(num , listOpen , listClose)  
                #    print("i:" , num) 
       
                #    print("candel0: " + f'{candel_state}') 
                   candel.append(candel_state)
                   if candel_state == "green": 
                        x_node = 23 - num
                        EP1.append(num + x_node)
                        EP1.append(num)
                        original_range = range(0, num)
                        reversed_range2 = list(original_range)[::-1]
                        # print("reversed_range2:" , reversed_range2)
                        for i2 in reversed_range2 :  
                            candel_state = Candel.candelstate(i2 , listOpen , listClose) 
                            # print("i2:" , i2)    
                            # print("candel1: " + f'{candel_state}')
                            candel.append(candel_state)
                        
                            if candel_state == "red":
                              
                              original_range = range(0, i2)
                              reversed_range3 = list(original_range)[::-1]
                            #   print("reversed_range3:" , reversed_range3)
                              for i3 in reversed_range3:  
                                   candel_state = Candel.candelstate(i3 , listOpen , listClose)   
                                #    print("i3:" , i3)   
                                #    print("candel2: " + f'{candel_state}')
                                   candel.append(candel_state)
                                   if candel_state == "green":
                                      x_node = i2 - i3
                                      EP1.append(i3 + x_node)
                                      EP1.append(i3)
                                      print("the end")
                                      x = 1
                                      break
       
                                   if x == 1:
                                     break    
                                      
                            if x == 1:
                                  break  
                   if x == 1:
                         break   

       prices_candel_close = []
       prices_candel_open = []
       time_candel = []
       times = []
        
       for index in EP1: 
            prices_candel_close.append(listClose[index])
            prices_candel_open.append(listOpen[index])
            time_candel.append(str (listTimestamp[index]))
            times.append(str (pd.to_datetime( listTimestamp[index] , unit='s')))                   
                           
      #  print ("candel:" , candel)
       
       EP1.reverse()
       candel.reverse()
       prices_candel_close.reverse()
       prices_candel_open.reverse()
       time_candel.reverse()
       times.reverse()
      #  print ("EP:" , EP1)
      #  print ("candel:" , candel)

       list_len = len(EP1)
      #  print("list_len:" , list_len)

       try:
         select_all = Database.select_table_All()
         print("select_all:" , select_all)
         if select_all == []:
          candel_num = 1 
         else:
              
              select_all_len = len(select_all)
              print("select_all_len:" , select_all_len)
              rec = select_all[select_all_len - 1]
              print("select_all:" , rec)
              candel_num = int (rec[1])
              print("rec:" , rec)
              candel_num = candel_num + 1
              print("candel_num:" , candel_num)

       except:
          print("erooooor select_all")

       if list_len == 4 and x == 1:
            end = EP1[0]
            point4 = EP1[3]
            print("end:" , end)
            time_end_pattern =  listTimestamp [end]  
            time_start_patern = listTimestamp [point4]
            # print("time_end_pattern:" , time_end_pattern)
            time_end_pattern = time_end_pattern + 21600
            # print("time_end_pattern:" , time_end_pattern)
            time_start_patern = time_start_patern + 1800
            # print("time_start_patern:" , time_start_patern)

            EP1 = json.dumps(EP1)
            candel = json.dumps(candel)
            prices_candel_close = json.dumps(prices_candel_close)
            prices_candel_open = json.dumps(prices_candel_open)
            time_candel = json.dumps(time_candel)
            times = json.dumps(times)
            value = (candel_num , "Two_Bottom" , EP1 , "" , "" , ""  , candel , prices_candel_open ,prices_candel_close , "" , "" , "" , "" , "false", "true" , "false" , time_start_patern , time_end_pattern ,time_candel , times , "" , "" , "")
            Database.insert_table(value)


   def candel_state_color(candel_state , listOpen , listClose , listTimestamp):
       
       if candel_state == "red":
         Candel_pos.candel_red(listOpen , listClose , listTimestamp)
         print ("red")

       elif candel_state == "green":
         Candel_pos.candel_green(listOpen , listClose , listTimestamp)    
         print ("green")    
       