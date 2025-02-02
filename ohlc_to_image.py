#!/usr/bin/env python
# coding: utf-8

# In[19]:


import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import time
from datetime import datetime, timedelta, timezone, date
import order_manager
import plotly.graph_objects as go
import pandas as pd
import os
import glob

with open("parameters.txt", "r") as file:
    exec(file.read())


# In[20]:


#DROP THE UNNCESSARY COLUMNS IN THE DATAFRAME AND CONVERTING THE TIME TO HUMAN READABLE FORMAT
def df_convert_hr(rates_frame_input):
    rates_frame_input['time'] = pd.to_datetime(rates_frame_input['time'], unit='s')
    rates_frame_input.drop(["tick_volume", "spread", "real_volume"], inplace=True, axis=1)
    rates_frame_input["time"] = pd.to_datetime(rates_frame_input["time"])
    return rates_frame_input


# In[21]:


def save_and_print_screenshot_rates_frame(rates_frame, timeframe):
    today_date = datetime.today().strftime('%Y-%m-%d')
    df = rates_frame
    folder_path = f"./OHLC_snapshots/{symbol}_{today_date}"
    os.makedirs(folder_path, exist_ok=True)
    
    # Create a candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='green', decreasing_line_color='red'
    )])

    if timeframe == 1:
        title=f"{symbol} OHLC 1 minute chart."
    elif timeframe == 15:
        title=f"{symbol} OHLC 15 minute chart."
    elif timeframe == mt5.TIMEFRAME_H1:
        title=f"{symbol} OHLC 1 hour chart."
    
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False  # Hide range slider
    )

    # Get current date and time in MMDDYYYY-HH-MM format
    current_time = datetime.now().strftime('%m%d%Y-%H-%M')
    
    # Save the figure as a static image (png, jpeg, etc.)
    # fig.update_layout(xaxis=dict(type='category'))
    fig.write_image(f"./OHLC_snapshots/{symbol}_{today_date}/{symbol}_ohlc_chart_{timeframe}_{current_time}.png")


# In[22]:


def download_rates_frame():
    global rates_frame_M1, rates_frame_M15, rates_frame_H1
    timeframe = mt5.TIMEFRAME_M1
    
    #GETTING THE TIMESTAMP FOR TODAY AND YESTERDAY
    utc_to = datetime.now() - timedelta(minutes=1) + timedelta(hours=2)
    utc_from = utc_to - timedelta(hours=2)
    startdate=utc_from.strftime('%Y%m%d')
    enddate=utc_to.strftime('%Y%m%d')
    
    # Get the OHLC data FOR TODAY AND YESTERDAY
    rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
    # Check if the data is downloaded successfully
    if rates is None:
        print("No data available, error code =", mt5.last_error())
    else:
        # Convert the data to a pandas DataFrame
        rates_frame = pd.DataFrame(rates)
        rates_frame_M1 = df_convert_hr(rates_frame)
    
    
    timeframe = mt5.TIMEFRAME_M15
    
    #GETTING THE TIMESTAMP FOR TODAY AND YESTERDAY
    utc_to = datetime.now() - timedelta(minutes=1) + timedelta(hours=2)
    utc_from = utc_to - timedelta(hours=24)
    startdate=utc_from.strftime('%Y%m%d')
    enddate=utc_to.strftime('%Y%m%d')
    
    # Get the OHLC data FOR TODAY AND YESTERDAY
    rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
    # Check if the data is downloaded successfully
    if rates is None:
        print("No data available, error code =", mt5.last_error())
    else:
        # Convert the data to a pandas DataFrame
        rates_frame = pd.DataFrame(rates)
        rates_frame_M15 = df_convert_hr(rates_frame)
    
    
    timeframe = mt5.TIMEFRAME_H1
    
    #GETTING THE TIMESTAMP FOR TODAY AND YESTERDAY
    utc_to = datetime.now() - timedelta(minutes=1) + timedelta(hours=2)
    utc_from = utc_to - timedelta(hours=132) 
    startdate=utc_from.strftime('%Y%m%d')
    enddate=utc_to.strftime('%Y%m%d')
    
    rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
    # Check if the data is downloaded successfully
    if rates is None:
        print("No data available, error code =", mt5.last_error())
    else:
        # Convert the data to a pandas DataFrame
        rates_frame = pd.DataFrame(rates)
        rates_frame_H1 = df_convert_hr(rates_frame)


# In[23]:


def save_rates_frame_1_15_60():
    today_date = datetime.today().strftime('%Y-%m-%d')
    download_rates_frame()
    save_and_print_screenshot_rates_frame(rates_frame_M1, 1)
    save_and_print_screenshot_rates_frame(rates_frame_M15, 15)
    save_and_print_screenshot_rates_frame(rates_frame_H1, mt5.TIMEFRAME_H1)
    folder_path = f"./OHLC_snapshots/{symbol}_{today_date}"
    patterns = [
        f"{symbol}_ohlc_chart_1_*",
        f"{symbol}_ohlc_chart_15_*",
        f"{symbol}_ohlc_chart_16385_*"
    ]
    # Function to get the latest file for a given pattern
    def get_latest_file(pattern):
        files = glob.glob(os.path.join(folder_path, pattern))
        if files:
            return max(files, key=os.path.getmtime)
        return None
    # Get the latest file for each pattern
    latest_files = {pattern: get_latest_file(pattern) for pattern in patterns}
    
    filename_m1 = get_latest_file(patterns[0])
    filename_m15 = get_latest_file(patterns[1])
    filename_16385 = get_latest_file(patterns[2])
    
    return filename_m1, filename_m15, filename_16385

