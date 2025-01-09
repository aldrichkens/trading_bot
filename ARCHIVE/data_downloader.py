#!/usr/bin/env python
# coding: utf-8

# In[26]:


import numpy
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime


# In[27]:


# Initialize the connection
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()


# In[28]:


#INPUTS
# SYMBOLS = AUDSD, EURUSD,EURJPY, XAUUSD, EURGPY, USDJPY
#symbol = input("Choose one AUDSD, EURUSD,EURJPY, XAUUSD, EURGBP, USDJPY.... :").upper()
symbol = ["AUDUSD","EURUSD","EURJPY","XAUUSD","EURGBP","USDJPY"]
timeframe = mt5.TIMEFRAME_M1  # 1-minute timeframe
year = int(input("year: "))
start_month = int(input("start month: "))
start_dom = int(input("start day of  the month: "))
end_month = int(input("end month: "))
end_dom = int(input("end day of  the month: "))
utc_from = datetime(year, start_month, start_dom)
utc_to = datetime(year, end_month, end_dom)


# In[29]:


startdate=utc_from.strftime('%Y%m%d')
enddate=utc_to.strftime('%Y%m%d')

for symbol in symbol:
    # Get the OHLC data
    rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
    
    # Check if the data is downloaded successfully
    if rates is None:
        print("No data available, error code =", mt5.last_error())
    else:
        # Convert the data to a pandas DataFrame
        rates_frame = pd.DataFrame(rates)
        # Convert the time in seconds to a datetime format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame.drop(["tick_volume", "spread", "real_volume"], inplace=True, axis=1)
    rates_frame["date"] = rates_frame["time"].astype("str").str[:10]
    rates_frame["time"] = rates_frame["time"].astype("str").str[11:16]
    rates = rates_frame.reindex(labels=["date", "time", "open", "high", "low", "close"], axis = 1)
    rates.to_csv(f'./{symbol}_{startdate}_{enddate}.csv', index=False)
