#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone, date
from scipy.signal import find_peaks
import time


# In[ ]:


with open("parameters.txt", "r") as file:
    exec(file.read())


# In[3]:


#Functions of the buy diagram ratio module

def convert_maxima_to_LL_LH_df(Pay, p1_range_localmaximas):
    Pa = p1_range_localmaximas[p1_range_localmaximas['high'] == Pay].drop(['open','low','close'], axis=1)
    Pa = Pa.drop_duplicates(subset=['high'], keep='last')
    Pa = Pa.rename(columns={"high":"price"})
    return Pa
    
def convert_minima_to_LL_LH_df(Pay, condition, p1_range_localminimas):
    Pa = p1_range_localminimas[(p1_range_localminimas['low'] == Pay) & condition].drop(['open','high','close'], axis=1)  
    Pa = Pa.drop_duplicates(subset=['low'], keep='last')
    Pa = Pa.rename(columns={"low":"price"})
    return Pa

def compute_index_Pa_x(Pay, p1_range_localmaximas):
    try:
        Pay_index = p1_range_localmaximas[p1_range_localmaximas['high'] == Pay].index[-1]
    except IndexError as IE:
        Pay_index = None
    return Pay_index


def create_tuples_p1_p3(df):
    p1_p2_p3 = []
    max_index = df.index.max()
    no_of_comb = ((max_index + 1) // 2) -1  # +1 to include the last element for odd lengths
    for i in range(no_of_comb):
        p1_p2_p3.append((max_index, max_index - 2*(i+1) + 1, max_index - 2*(i+1)))
    return p1_p2_p3

def create_empty_p1_and_p2_and_p3_df():
    p1 = pd.DataFrame(columns=['time','price'])
    p1 = pd.DataFrame({'time': pd.Series(dtype='datetime64[ns]'), 'price': pd.Series(dtype='float')})
    p2 = pd.DataFrame(columns=['time','price'])
    p2 = pd.DataFrame({'time': pd.Series(dtype='datetime64[ns]'), 'price': pd.Series(dtype='float')})
    p3 = pd.DataFrame(columns=['time','price'])
    p3 = pd.DataFrame({'time': pd.Series(dtype='datetime64[ns]'), 'price': pd.Series(dtype='float')})
    return p1, p2, p3

def create_empty_time_price_df():
    df = pd.DataFrame(columns=['time','price'])
    df = pd.DataFrame({'time': pd.Series(dtype='datetime64[ns]'), 'price': pd.Series(dtype='float')})
    return df

def create_empty_time_open_high_low_close_df():
    df = pd.DataFrame(columns=['time','open','high','low','close'])
    df = pd.DataFrame({'time': pd.Series(dtype='datetime64[ns]'), 'open': pd.Series(dtype='float'),
                      'high': pd.Series(dtype='float'), 'low': pd.Series(dtype='float'),
                      'close': pd.Series(dtype='float')})
    return df


# In[16]:


# FUNCTION TO DETECT P1 P2 P3 for the EXTERNAL AND INTERNAL
def obtain_p1_p2_p3(rates_frame_p3):
    #obtaining the maximum point from the last 110 minutes for sells
    Max_110_y = rates_frame_p3["high"].max()
    Max_110 = rates_frame_p3[rates_frame_p3["high"] == Max_110_y].iloc[[-1]]
    
    #obtaining the minimum point from the last 110 minutes for sells
    Min_110_y = rates_frame_p3["low"].min()
    Min_110 = rates_frame_p3[rates_frame_p3["low"] == Min_110_y].iloc[[-1]]
    
    # Creating a new dataframe for the start and end of the minimum points in order to grab the data of local maxima and minima in an uptrend
    p1_range_start_time = Max_110['time'].iloc[-1]
    p1_range_end_time = Min_110["time"].iloc[-1]
    mask = rates_frame_p3["time"].ge(p1_range_start_time) & rates_frame_p3["time"].le(p1_range_end_time)
    p1_range = rates_frame_p3[mask].reset_index(drop=True)
    
    # Find the index of local maximas
    local_maximas_i,_ = find_peaks(p1_range['high'].values)
    local_maximas_i = np.array(local_maximas_i)
    
    # Find the index of the local minima by inverting the data
    local_minimas_i,_ = find_peaks(-p1_range['low'].values)
    local_minimas_i = np.array(local_minimas_i)
    
    #Obtaining the dataframe of the local minimas and local maximas
    p1_range_localminimas = p1_range[p1_range.index.isin(local_minimas_i)].reset_index(drop=True)
    p1_range_localmaximas = p1_range[p1_range.index.isin(local_maximas_i)].reset_index(drop=True)
    
    # Finding the value of Pay1
    Pay1 = Max_110_y
    
    #to find the y value of the possible 2nd local minima:
    Pay3 = p1_range_localmaximas["high"].max()
    
    Pay3_index = compute_index_Pa_x(Pay3, p1_range_localmaximas)
    Pay3_index_range = Pay3_index
    
    while True:
        #finding the index of the 1st local minima in the series "p1_range_localminimas" as P2
        condition1 = p1_range_localminimas["time"].ge(p1_range.iloc[0,0])
        condition2 = p1_range_localminimas["time"].le(p1_range_localmaximas.iloc[Pay3_index,0])
        condition = condition1 & condition2
        
        Pay2 = p1_range_localminimas[condition == True]['low'].values
    
        try:
            #finding the index of the 1st local minima in the series "p1_range_localminimas" as P2
            condition1 = p1_range_localminimas["time"].ge(p1_range.iloc[0,0])
            condition2 = p1_range_localminimas["time"].le(p1_range_localmaximas.iloc[Pay3_index,0])
            condition = condition1 & condition2
        
            #to find the y value of the 1st local maxima:
            Pay2 = p1_range_localminimas[condition == True]['low'].values
            if len(Pay2) == 0:
                #proceed with the next pay3 index and rerun the while loop
                Pay3_index_range = Pay3_index_range + 1
                Pay3 = p1_range_localmaximas.iloc[Pay3_index_range:,2].max()
                Pay3_index = compute_index_Pa_x(Pay3, p1_range_localmaximas)
                continue
            else:
                #if value exists, find the minimum
                Pay2 = min(Pay2)
                break
        except IndexError as err1:
            break
        except ValueError as ve:
            continue
        except TypeError as te:
            break
    
            
    #Making a new dataframe of the higher highs and higher lows approaching P3 in chronological order
    LL_LH = create_empty_time_price_df()
    
    #Grabbing the data attached to Pay*
    mask = rates_frame_p3['high'] == Pay1
    pa1 = rates_frame_p3[mask].drop(['open','low','close'], axis=1).drop_duplicates(subset=['high'], keep='last').rename(columns={"high":"price"})
    LL_LH_df = pd.concat([LL_LH, pa1], ignore_index=True)
    
    Pa2 = p1_range_localminimas[p1_range_localminimas['low'] == Pay2].drop(['open','high','close'], axis=1)
    Pa2 = Pa2.drop_duplicates(subset=['low'], keep='last')
    Pa2 = Pa2.rename(columns={"low":"price"})
    LL_LH_df = pd.concat([LL_LH_df, Pa2], ignore_index=True)
    LL_LH_df = pd.concat([LL_LH_df, convert_maxima_to_LL_LH_df(Pay3, p1_range_localmaximas)], ignore_index=True)
    
    #Resetting the values to avoid issues
    Pay2 = Pay1_index = Pay3_index = 0
    
    #Assigning new values to find new sets of Pa2, Pa3
    Pay1 = Pay3
    Pay1_index = compute_index_Pa_x(Pay1, p1_range_localmaximas)
    
    #Resetting the values to avoid issues
    Pay3 = Pay3_index = 0
    
    #Finding the initial value of Pay3
    try:
        Pay3 = p1_range_localmaximas.iloc[Pay1_index+1:,2].max()
        Pay3_index = compute_index_Pa_x(Pay3, p1_range_localmaximas)
    except IndexError as err1:
        print('There is no next p3. Continue with the external P1-P2-P3...')
        Pay3 = None
    
    if Pay3 != None:
        #Finding the values of the lower lows and lower highs and appending it to the LL_HH_df
        while True:
            Pay3_index_range = 0
            try:
                # Check if the current Pay3_index is beyond the end of p1_range_localminimas
                if Pay3_index > len(p1_range_localmaximas):
                    print(f"End of p1_range_localmaximas reached.{Pay3_index}")
                    break
                    
                #finding the index of the next local maxima
                condition1 = p1_range_localminimas["time"].ge(p1_range_localmaximas.iloc[Pay1_index,0])
                condition2 = p1_range_localminimas["time"].le(p1_range_localmaximas.iloc[Pay3_index,0])
                condition = condition1 & condition2
        
                
                #to find the y value of the next local minima:
                Pay2 = p1_range_localminimas[condition == True]['low'].values
                
                #previous ll index
                pLL_index = LL_LH_df[LL_LH_df['price'] == Pay1].index[0] - 1
                pLLy = LL_LH_df.iloc[pLL_index,1]
        
                #if Pay2 isnt existing for the current Pay3
                condition3 = len(Pay2) == 0
                
                #if the current Pay2 is more than the previous ll
                try:
                    condition4 = p1_range_localminimas[condition == True]['low'].values.min() > pLLy
                except ValueError as err2:
                    Pay3_index = Pay3_index+1
                    Pay3 = p1_range_localmaximas.iloc[Pay3_index:,2].max()
                    Pay3_index = compute_index_Pa_x(Pay3, p1_range_localmaximas)
                    continue
                    
                if condition3 or condition4:
                    #proceed with the next pay3 index and rerun the while loop
                    Pay2 = 0
                    Pay3_index_range = Pay3_index+1
                    Pay3 = p1_range_localmaximas.iloc[Pay3_index_range:,2].max()
                    Pay3_index = compute_index_Pa_x(Pay3, p1_range_localmaximas)
                    continue
                else:
                    Pay2=Pay2.min()
                    #Appending to the LL_LH_df 
                    condition5 = (p1_range_localminimas['low'] == Pay2) & condition
                    LL_LH_df = pd.concat([LL_LH_df, convert_minima_to_LL_LH_df(Pay2, condition5, p1_range_localminimas)], ignore_index=True)
                    LL_LH_df = pd.concat([LL_LH_df, convert_maxima_to_LL_LH_df(Pay3, p1_range_localmaximas)], ignore_index=True)
                    
                    #Assigning new values to find new sets of Pa2, Pa3
                    Pay1 = Pay3
                    Pay1_index = compute_index_Pa_x(Pay1, p1_range_localmaximas)
                    
                    #Finding the initial value of Pay3
                    Pay3 = p1_range_localmaximas.iloc[Pay1_index+1:,2].max()
                    Pay3_index = compute_index_Pa_x(Pay3, p1_range_localmaximas)
                    continue
            except IndexError as err1:
                break
            except TypeError as te:
                break
    
        #Append Max_110 to the dataframe:
        Min_110 = Min_110.drop(['open','high','close'], axis=1).rename(columns={"low":"price"})
        LL_LH_df = pd.concat([LL_LH_df, Min_110], ignore_index=True)
        
        # Create a tuple combining the list of possible p1-p2-p3 (initial values)
        p1_p2_p3i = create_tuples_p1_p3(LL_LH_df)
        
        # finding the right p1-p2-p3 in terms of ratios
        p1_p2_p3_index = []
        for i in p1_p2_p3i:
            p3i=i[0]
            p2i=i[1]
            p1i=i[2]
            p3y_p2y = LL_LH_df.iloc[p3i,1] - LL_LH_df.iloc[p2i,1]
            p2y_p1y = LL_LH_df.iloc[p2i,1] - LL_LH_df.iloc[p1i,1]
            p3x_p2x = LL_LH_df.iloc[p3i,0] - LL_LH_df.iloc[p2i,0]
            p2x_p1x = LL_LH_df.iloc[p2i,0] - LL_LH_df.iloc[p1i,0]
        
            # conditions for finding the right p1-p2-p3
            condition1 = 1.027 <= abs(p3y_p2y/p2y_p1y) <= 1.9286
            try:
                condition2 = 0.217 <= abs(p3x_p2x/p2x_p1x) <= 5
            except ZeroDivisionError as err1:
                condition2 = False
                
            condition3 = p2x_p1x > pd.Timedelta(minutes=1)
            condition4 = pd.Timedelta(minutes=2) <= p2x_p1x <= pd.Timedelta(minutes=24)
            condition5 = pd.Timedelta(minutes=2) <= p3x_p2x <= pd.Timedelta(minutes=21)
            condition = condition1 & condition2 & condition3 & condition4 & condition5
            
            if condition:
                p1_p2_p3_index.append(i)
    
            p1, p2, p3 = create_empty_p1_and_p2_and_p3_df()
        
        if len(p1_p2_p3_index) == 0:
            return p1_range_localminimas, p1_range_localmaximas, LL_LH_df, p1, p2, p3
            
        else:
            for p3i, p2i, p1i in p1_p2_p3_index:
                new_p3 = LL_LH_df.iloc[[p3i]]
                new_p2 = LL_LH_df.iloc[[p2i]]
                new_p1 = LL_LH_df.iloc[[p1i]]
                p3 = pd.concat([p3,new_p3], ignore_index=True)
                p2 = pd.concat([p2,new_p2], ignore_index=True)
                p1 = pd.concat([p1,new_p1], ignore_index=True)
                return  p1_range_localminimas, p1_range_localmaximas, LL_LH_df, p1, p2, p3
        
        if len(p1) != len(p2):
            print("Index error! P1 and P2 doesn't match!")
            return p1_range_localminimas, p1_range_localmaximas, LL_LH_df, p1, p2, p3
            
    elif Pay3 == None:
        p1, p2, p3 = create_empty_p1_and_p2_and_p3_df()
        return p1_range_localminimas, p1_range_localmaximas, LL_LH_df, p1, p2, p3


# In[17]:


def validate_and_buy(rates_frame_p3, p3_rates_frame, buy_tp):
    TP1_price = None
    # OBTAINING THE EXTERNAL p1-p2-p3
    (
        p1_range_localminimas,
        p1_range_localmaximas,
        LL_LH_df,
        p1,
        p2,
        p3
    ) = obtain_p1_p2_p3(rates_frame_p3)

    
    # FINDING THE VALUES OF THE OHLC DATAFRAME FROM THE EXTERNAL P2 AND P3 to HAVE THE INTERNAL P1-P2-P3
    if not len(p1) == 0 and not len(p2) == 0:
        p1_internal_range_start_time = p2["time"].iloc[-1]
        p1_internal_range_end_time = p3["time"].iloc[-1]
        
        mask = (p1_internal_range_start_time <= rates_frame_p3["time"]) & (rates_frame_p3["time"] <= p1_internal_range_end_time)
        p1_internal_range = rates_frame_p3[mask]
    
    try: 
        (
            p1_range_localminimas_internal,
            p1_range_localmaximas_internal,
            LL_LH_df_internal, p1_internal,
            p2_internal,
            p3_internal
        ) = obtain_p1_p2_p3(p1_internal_range)
    except (TypeError, ValueError) as TE_VE:
        p1_internal, p2_internal, p3_internal = create_empty_p1_and_p2_and_p3_df()
        p1_range_localminimas_internal = p1_range_localmaximas_internal = create_empty_time_open_high_low_close_df()
        LL_LH_internal = create_empty_time_price_df()
    except UnboundLocalError as ULE:
        #if there is no p1-p2-p3 because of the time limits, it will return a ULE, therefore, find the p1-p2-p3 with another dataframe
        #tail 42 is just temporary, gather more data for this
        p1_internal_range = rates_frame_p3.tail(42)
    
        try:
            (
                p1_range_localminimas_internal,
                p1_range_localmaximas_internal,
                LL_LH_df_internal, p1_internal,
                p2_internal,
                p3_internal
            ) = obtain_p1_p2_p3(p1_internal_range)
        except (TypeError, UnboundLocalError) as TE_ULE:
            p1_internal, p2_internal, p3_internal = create_empty_p1_and_p2_and_p3_df()
            p1_range_localminimas_internal = p1_range_localmaximas_internal = create_empty_time_open_high_low_close_df()
            LL_LH_df_internal = create_empty_time_price_df()
			
    
    # APPEND THE VALUES OF THE INTERNAL P1, P2, P3 to the external one. 
    p1 = pd.concat([p1,p1_internal], ignore_index=True)
    p2 = pd.concat([p2,p2_internal], ignore_index=True)
    p3 = pd.concat([p3,p3_internal], ignore_index=True)
    
    #SETTING THE INITIAL VALUE OF BUY TO "NONE"
    Buy = None
    
    if (len(p1) == 0 and len(p2) == 0) and (len(p1) != len(p2)):
        Buy = False
        SL_price = None
        OB_size = None
        Entry_price = None
        SL_size = None
        p2_bos = p4 = create_empty_time_price_df()
        return Buy, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4
        
    try:
		#FINDING P4 RANGE DATAFRAME
        p4_range = p3_rates_frame
        
        #FIND THE INITIAL VALUE OF P4 ( MINIMUM LOW IN THE P4 RANGE)
        p4y = p4_range["high"].max()
        mask = p4_range["high"] == p4y
        p4 = p4_range[mask].drop(['open','low','close'], axis=1).rename(columns={"high":"price"}).iloc[[-1]]
        
        # FINDING EVERY POSSIBLE P2 AFTER BOS (IF THERE IS A BOS)
        p4y = p4["price"].iloc[0]
        p2_index = 0
        p2_bos = create_empty_time_price_df()

    except IndexError as IE:
        Buy = False
        SL_price = None
        OB_size = None
        Entry_price = None
        SL_size = None
        p2_bos = p4 = create_empty_time_price_df()
        return Buy, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4
		
    while p2_index < len(p2):
        if p2["price"].iloc[p2_index] < p4y:
            #GRAB THE INDIVIDUAL P2 THAT CAUSED BOS
            p2_bos = pd.concat([p2_bos,p2.iloc[[p2_index]]], ignore_index=True)
            p2_index += 1
        else:
            p2_index += 1
            continue  
            
    
    # DECIDING WHETHER TO BUY OR NOT
    if len(p2_bos) == 0:
        Buy = False
        SL_price = None
        OB_size = None
        Entry_price = None
        SL_size = None
        return Buy, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4
    else:
        SL_price = p3["price"].iloc[0] - breathing_room
        OB_size = round(p2_bos["price"].max() - p3["price"].iloc[0], pip_precision)
        Entry_price = round(p2_bos["price"].max() - 0.6*OB_size + breathing_room, pip_precision)
        SL_size = round(Entry_price - SL_price, pip_precision)
        TP1_price = round(Entry_price + (SL_size * RR_value), pip_precision)
        TP_size = buy_tp - Entry_price
        RR = TP_size / SL_size
    
        if RR >= RR_value:
            Buy = True
            return Buy, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4
        else:
            Buy = False
            return Buy, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4


# In[18]:


# verify p4 before entry:
def verify_p4(p2_bos,p3,p4,p3_rates_frame):
    number_of_rows = p3.shape[0]
    p4 = pd.concat([p4] * number_of_rows, ignore_index=True)
    p4.reset_index(drop=True)
    p4_is_valid = []
    
    for index, row in p2_bos.iterrows():
        # OBTAINING THE PRICE AND TIME OF P2_BOS, P3 AND P4 and their difference
        p4x = p4['time'].iloc[index]
        p4y = p4['price'].iloc[index]
        p3x = p3['time'].iloc[index]
        p3y = p3['price'].iloc[index]
        p2_bos_x = p2_bos['time'].iloc[index]
        p2_bos_y = p2_bos['price'].iloc[index]
        p4y_p3y = abs(p4y - p3y)
        p3y_p2_bos_y = abs(p3y - p2_bos_y)
        p3y_p4y = abs(p3y - p4y)
        p2_bos_x_p3x = abs(p3x - p2_bos_x)
        p3x_p4x = abs(p4x - p3x)
            
        # OBTAIN THE p4_rates_frame DATAFRAME:
        mask = p3_rates_frame['time'] >= p4x
        p4_rates_frame = p3_rates_frame[mask]
        
        #OBTAIN P5
        p5y = p4_rates_frame["low"].min()
        mask = p4_rates_frame['low'] == p5y
        p5 = p4_rates_frame[mask].iloc[0]
        p5x = p5['time'] #time of p5
        
        # OBTAIN P3-P5 RATES FRAME
        mask = (p3_rates_frame['time'] >= p3x) & (p3_rates_frame['time'] <= p5x)
        p3_p5_rates_frame = p3_rates_frame[mask]
        
        # Obtain the lows in P3-P5 RATES FRAME that are below the P2_BOS_Y
        mask = p3_p5_rates_frame['high'] > p2_bos_y
        p3_p5_rates_frame_lows_below_p2_bos = p3_p5_rates_frame[mask]
        
        # calculate the time that price spent on the other side of the p2_bos:
        bos_first_point_time = p3_p5_rates_frame_lows_below_p2_bos["time"].iloc[0]
        bos_last_point_time = p3_p5_rates_frame_lows_below_p2_bos["time"].iloc[-1]
        bos_time = bos_last_point_time - bos_first_point_time
        
        # OBTAINING THE RATIOS TO VALIDATE P4
        condition1 = pd.Timedelta(minutes=1) <= (p4x - p3x) <= pd.Timedelta(minutes=33)
        condition2 = 0.167 <= (p3x_p4x/p2_bos_x_p3x) <= 4.5
        condition3 = 1.0219 <= (p4y_p3y/p3y_p2_bos_y) <= 1.8889
        condition4 = pd.Timedelta(minutes=0) <= bos_time <= pd.Timedelta(minutes=17)
        condition = condition1 & condition2 & condition3 & condition4
        
        if condition:
            is_valid = True
        elif condition == False:
            is_valid = False
        p4_is_valid.append(is_valid)
    result = any(p4_is_valid)
    return result

