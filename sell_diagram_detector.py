#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone, date
from scipy.signal import find_peaks
import time


# In[2]:


#Functions of the sell diagram ratio module

def convert_minima_to_HH_HL_df(Pay, p1_range_localminimas):
    Pa = p1_range_localminimas[p1_range_localminimas['low'] == Pay].drop(['open','high','close'], axis=1)
    Pa = Pa.drop_duplicates(subset=['low'], keep='last')
    Pa = Pa.rename(columns={"low":"price"})
    return Pa

def convert_maxima_to_HH_HL_df(Pay, condition, p1_range_localmaximas):
    Pa = p1_range_localmaximas[(p1_range_localmaximas['high'] == Pay) & condition].drop(['open','low','close'], axis=1)  
    Pa = Pa.drop_duplicates(subset=['high'], keep='last')
    Pa = Pa.rename(columns={"high":"price"})
    return Pa

def compute_index_Pa_n(Pay, p1_range_localminimas):
    try:
        Pay_index = p1_range_localminimas[p1_range_localminimas['low'] == Pay].index[-1]
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


# In[5]:


# FUNCTION TO DETECT P1 P2 P3 for the EXTERNAL AND INTERNAL
def obtain_p1_p2_p3(Last_110):
    #obtaining the maximum point from the last 110 minutes for sells
    Max_110_y = Last_110["high"].max()
    Max_110 = Last_110[Last_110["high"] == Max_110_y].iloc[[-1]]
    
    #obtaining the minimum point from the last 110 minutes for sells
    Min_110_y = Last_110["low"].min()
    Min_110 = Last_110[Last_110["low"] == Min_110_y].iloc[[-1]]
    
    # Creating a new dataframe for the start and end of the minimum points in order to grab the data of local maxima and minima in an uptrend
    p1_range_start_time = Min_110["time"].iloc[-1]
    p1_range_end_time = Max_110['time'].iloc[-1]
    mask = Last_110["time"].ge(p1_range_start_time) & Last_110["time"].le(p1_range_end_time)
    p1_range = Last_110[mask].reset_index(drop=True)
    
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
    Pay1 = Min_110_y
    
    #to find the y value of the possible 2nd local minima:
    Pay3 = p1_range_localminimas["low"].min()
    Pay3_index = compute_index_Pa_n(Pay3, p1_range_localminimas)
    Pay3_index_range = Pay3_index
    
    while True:
        try:
            #finding the index of the 1st local maxima in the series "p1_range_localmaxima" as P2
            condition1 = p1_range_localmaximas["time"].ge(p1_range.iloc[0,0])
            condition2 = p1_range_localmaximas["time"].le(p1_range_localminimas.iloc[Pay3_index,0])
            condition = condition1 & condition2
            
            #to find the y value of the 1st local maxima:
            Pay2 = p1_range_localmaximas[condition == True]['high'].values
            if len(Pay2) == 0:
                #proceed with the next pay3 index and rerun the while loop
                Pay3_index_range = Pay3_index_range + 1
                Pay3 = p1_range_localminimas.iloc[Pay3_index_range:,3].min()
                Pay3_index = compute_index_Pa_n(Pay3, p1_range_localminimas)
                continue
            else:
                #if value exists, find the maximum
                Pay2 = max(Pay2)
                break
        except IndexError as err1:
            break
        except ValueError as ve:
            break
        except TypeError as te:
            break
    
            
    #Making a new dataframe of the higher highs and higher lows approaching P3 in chronological order
    HH_HL_df = create_empty_time_price_df()
    
    #Grabbing the data attached to Pay*
    mask = Last_110['low'] == Pay1
    pa1 = Last_110[mask].drop(['open','high','close'], axis=1).drop_duplicates(subset=['low'], keep='last').rename(columns={"low":"price"})
    HH_HL_df = pd.concat([HH_HL_df, pa1], ignore_index=True)
    
    Pa2 = p1_range_localmaximas[p1_range_localmaximas['high'] == Pay2].drop(['open','low','close'], axis=1)
    Pa2 = Pa2.drop_duplicates(subset=['high'], keep='last')
    Pa2 = Pa2.rename(columns={"high":"price"})
    HH_HL_df = pd.concat([HH_HL_df, Pa2], ignore_index=True)
    HH_HL_df = pd.concat([HH_HL_df, convert_minima_to_HH_HL_df(Pay3, p1_range_localminimas)], ignore_index=True)
    
    #Resetting the values to avoid issues
    Pay2 = Pay1_index = Pay3_index = 0
    
    #Assigning new values to find new sets of Pa2, Pa3
    Pay1 = Pay3
    Pay1_index = compute_index_Pa_n(Pay1, p1_range_localminimas)
    
    #Resetting the values to avoid issues
    Pay3 = Pay3_index = 0
    
    #Finding the initial value of Pay3
    try:
        Pay3 = p1_range_localminimas.iloc[Pay1_index+1:,3].min()
        Pay3_index = compute_index_Pa_n(Pay3, p1_range_localminimas)
    except IndexError as err1:
        print('There is no next p3. Continue with the external P1-P2-P3...')
        Pay3 = None

    if Pay3 != None:
        #Finding the values of the higher lows and higher highs and appending it to the HH_HL_df
        while True:
            Pay3_index_range = 0
            try:
                # Check if the current Pay3_index is beyond the end of p1_range_localminimas
                if Pay3_index > len(p1_range_localminimas):
                    print(f"End of p1_range_localminimas reached.{Pay3_index}")
                    break
                    
                #finding the index of the next local maxima
                condition1 = p1_range_localmaximas["time"].ge(p1_range_localminimas.iloc[Pay1_index,0])
                condition2 = p1_range_localmaximas["time"].le(p1_range_localminimas.iloc[Pay3_index,0])
                condition = condition1 & condition2
        
                
                #to find the y value of the next local maxima:
                Pay2 = p1_range_localmaximas[condition == True]['high'].values
                
                #previous HH index
                pHH_index = HH_HL_df[HH_HL_df['price'] == Pay1].index[0] - 1
                pHHy = HH_HL_df.iloc[pHH_index,1]
        
                #if Pay2 isnt existing for the current Pay3
                condition3 = len(Pay2) == 0
                
                #if the current Pay2 is less than the previous HH
                try:
                    condition4 = p1_range_localmaximas[condition == True]['high'].values.max() < pHHy
                except ValueError as err2:
                    Pay3_index = Pay3_index+1
                    Pay3 = p1_range_localminimas.iloc[Pay3_index:,3].min()
                    Pay3_index = compute_index_Pa_n(Pay3, p1_range_localminimas)
                    continue
                    
                if condition3 or condition4:
                    #proceed with the next pay3 index and rerun the while loop
                    Pay2 = 0
                    Pay3_index_range = Pay3_index+1
                    Pay3 = p1_range_localminimas.iloc[Pay3_index_range:,3].min()
                    Pay3_index = compute_index_Pa_n(Pay3, p1_range_localminimas)
                    continue
                else:
                    Pay2=Pay2.max()
                    #Appending to the HH_HL_df 
                    condition5 = (p1_range_localmaximas['high'] == Pay2) & condition
                    HH_HL_df = pd.concat([HH_HL_df, convert_maxima_to_HH_HL_df(Pay2, condition5, p1_range_localmaximas)], ignore_index=True)
                    HH_HL_df = pd.concat([HH_HL_df, convert_minima_to_HH_HL_df(Pay3, p1_range_localminimas)], ignore_index=True)
                    
                    #Assigning new values to find new sets of Pa2, Pa3
                    Pay1 = Pay3
                    Pay1_index = compute_index_Pa_n(Pay1, p1_range_localminimas)
                    
                    #Finding the initial value of Pay3
                    Pay3 = p1_range_localminimas.iloc[Pay1_index+1:,3].min()
                    Pay3_index = compute_index_Pa_n(Pay3, p1_range_localminimas)
                    continue
            except IndexError as err1:
                break
            except TypeError as te:
                break
    
    
        #Append Max_110 to the dataframe:
        Max_110 = Max_110.drop(['open','low','close'], axis=1).rename(columns={"high":"price"})
        HH_HL_df = pd.concat([HH_HL_df, Max_110], ignore_index=True)
        
        # Create a tuple combining the list of possible p1-p2-p3 (initial values)
        p1_p2_p3i = create_tuples_p1_p3(HH_HL_df)
        
        # finding the right p1-p2-p3 in terms of ratios
        p1_p2_p3_index = []
        for i in p1_p2_p3i:
            p3i=i[0]
            p2i=i[1]
            p1i=i[2]
            p3y_p2y = HH_HL_df.iloc[p3i,1] - HH_HL_df.iloc[p2i,1]
            p2y_p1y = HH_HL_df.iloc[p2i,1] - HH_HL_df.iloc[p1i,1]
            p3x_p2x = HH_HL_df.iloc[p3i,0] - HH_HL_df.iloc[p2i,0]
            p2x_p1x = HH_HL_df.iloc[p2i,0] - HH_HL_df.iloc[p1i,0]
        
            # conditions for finding the right p1-p2-p3
            condition1 = 1.027 <= abs(p3y_p2y/p2y_p1y) <= 1.9286
            try:
                condition2 = 0.217 <= p3x_p2x/p2x_p1x <= 5
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
            return p1_range_localminimas, p1_range_localmaximas, HH_HL_df, p1, p2, p3
            
        else:
            for p3i, p2i, p1i in p1_p2_p3_index:
                new_p3 = HH_HL_df.iloc[[p3i]]
                new_p2 = HH_HL_df.iloc[[p2i]]
                new_p1 = HH_HL_df.iloc[[p1i]]
                p3 = pd.concat([p3,new_p3], ignore_index=True)
                p2 = pd.concat([p2,new_p2], ignore_index=True)
                p1 = pd.concat([p1,new_p1], ignore_index=True)
                return  p1_range_localminimas, p1_range_localmaximas, HH_HL_df, p1, p2, p3
        
        if len(p1) != len(p2):
            print("Index error! P1 and P2 doesn't match!")
            return p1_range_localminimas, p1_range_localmaximas, HH_HL_df, p1, p2, p3
            
    elif Pay3 == None:
        p1, p2, p3 = create_empty_p1_and_p2_and_p3_df()
        return p1_range_localminimas, p1_range_localmaximas, HH_HL_df, p1, p2, p3


# In[6]:


def validate_and_sell(Last_110, sell_tp):
    TP1_price = None
    # OBTAINING THE EXTERNAL p1-p2-p3
    (
        p1_range_localminimas,
        p1_range_localmaximas,
        HH_HL_df,
        p1,
        p2,
        p3
    ) = obtain_p1_p2_p3(Last_110)
    
    # FINDING THE VALUES OF THE OHLC DATAFRAME FROM THE EXTERNAL P2 AND P3 to HAVE THE INTERNAL P1-P2-P3
    if not len(p1) == 0 and not len(p2) == 0:
        p1_internal_range_start_time = p2["time"].iloc[-1]
        p1_internal_range_end_time = p3["time"].iloc[-1]
        
        mask = (p1_internal_range_start_time <= Last_110["time"]) & (Last_110["time"] <= p1_internal_range_end_time)
        p1_internal_range = Last_110[mask]
        
    try: 
        (
            p1_range_localminimas_internal,
            p1_range_localmaximas_internal,
            HH_HL_df_internal, p1_internal,
            p2_internal,
            p3_internal
        ) = obtain_p1_p2_p3(p1_internal_range)
    except (TypeError, ValueError) as TE_VE:
        p1_internal, p2_internal, p3_internal = create_empty_p1_and_p2_and_p3_df()
        p1_range_localminimas_internal = p1_range_localmaximas_internal = create_empty_time_open_high_low_close_df()
        HH_HL_df_internal = create_empty_time_price_df()
    except UnboundLocalError as ULE:
        #if there is no p1-p2-p3 because of the time limits, it will return a ULE, therefore, find the p1-p2-p3 with another dataframe
        #tail 42 is just temporary, gather more data for this
        p1_internal_range = Last_110.tail(42)

        try:
            (
                p1_range_localminimas_internal,
                p1_range_localmaximas_internal,
                HH_HL_df_internal, p1_internal,
                p2_internal,
                p3_internal
            ) = obtain_p1_p2_p3(p1_internal_range)
        except (TypeError, UnboundLocalError) as TE_ULE:
            p1_internal, p2_internal, p3_internal = create_empty_p1_and_p2_and_p3_df()
            p1_range_localminimas_internal = p1_range_localmaximas_internal = create_empty_time_open_high_low_close_df()
            HH_HL_df_internal = create_empty_time_price_df()
        
            
    
    # APPEND THE VALUES OF THE INTERNAL P1, P2, P3 to the external one. 
    p1 = pd.concat([p1,p1_internal], ignore_index=True)
    p2 = pd.concat([p2,p2_internal], ignore_index=True)
    p3 = pd.concat([p3,p3_internal], ignore_index=True)
    
    #SETTING THE INITIAL VALUE OF SELL TO "NONE"
    Sell = None
    
    if (len(p1) == 0 and len(p2) == 0) and (len(p1) != len(p2)):
        Sell = False
        SL_price = None
        OB_size = None
        Entry_price = None
        SL_size = None
        p2_bos = p4 = create_empty_time_price_df()
        return Sell, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4
        
    try:
        #FINDING P4 RANGE DATAFRAME
        p4_range_start_time = p3["time"].iloc[-1]
        p4_range_end_time = Last_110["time"].iloc[-1]
        mask = (p4_range_start_time <= Last_110["time"]) & (Last_110["time"] <= p4_range_end_time)
        p4_range = Last_110[mask]
        
        #FIND THE INITIAL VALUE OF P4 ( MINIMUM LOW IN THE P4 RANGE)
        p4y = p4_range["low"].min()
        mask = p4_range["low"] == p4y
        p4 = p4_range[mask].drop(['open','high','close'], axis=1).rename(columns={"low":"price"}).iloc[[-1]]
        
        # FINDING EVERY POSSIBLE P2 AFTER BOS (IF THERE IS A BOS)
        p4y = p4["price"].iloc[0]
        p2_index = 0
        p2_bos = create_empty_time_price_df()
    except IndexError as IE:
        Sell = False
        SL_price = None
        OB_size = None
        Entry_price = None
        SL_size = None
        p2_bos = p4 = create_empty_time_price_df()
        return Sell, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4
        
    while p2_index < len(p2):
        if p2["price"].iloc[p2_index] > p4y:
            #GRAB THE INDIVIDUAL P2 THAT CAUSED BOS
            p2_bos = pd.concat([p2_bos,p2.iloc[[p2_index]]], ignore_index=True)
            p2_index += 1
        else:
            p2_index += 1
            continue  
            
    
    # DECIDING WHETHER TO SELL OR NOT
    if len(p2_bos) == 0:
        Sell = False
        SL_price = None
        OB_size = None
        Entry_price = None
        SL_size = None
        return Sell, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4
    else:
        SL_price = p3["price"].iloc[0] + 0.00007
        OB_size = round(p3["price"].iloc[0] - p2_bos["price"].min(), 5)
        Entry_price = round(p2_bos["price"].min() + 0.6*OB_size - 0.00007, 5)
        SL_size = round(SL_price - Entry_price, 5)
        TP1_price = round(Entry_price - (SL_size * 5), 5)
        TP_size = Entry_price - sell_tp
        RR = TP_size / SL_size

        if RR >= 5:
            Sell = True
            return Sell, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4
        else:
            Sell = False
            return Sell, SL_price, TP1_price, OB_size, Entry_price, SL_size, p1, p2, p2_bos, p3, p4

